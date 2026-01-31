import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from google import genai
import logging
import concurrent.futures
import socket
import re

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# You might want to move API keys to environment variables in a real app
API_KEY = "AIzaSy..." # REDACTED

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Google GenAI Client: {e}")
    client = None

# Global DB Connection (Per-user connections are better for multi-user apps, 
# but for this local app we'll store a single global connection or re-connect per request)
# For simplicity in this demo, we'll store credentials in a global dict and reconnect on query.
# Thread pool for non-blocking DB connections
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

# Global DB Connection
db_config = {}
db_schema = ""  # Store schema info

@app.before_request
def log_request():
    logger.info(f"Incoming request: {request.method} {request.url} - Origin: {request.headers.get('Origin')}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/connect', methods=['POST'])
def connect_database():
    data = request.json
    global db_config
    
    host = data.get('host')
    port = int(data.get('port', 3306))
    user = data.get('user')
    password = data.get('password')
    database = data.get('database')
    
    # FORCE TCP: Convert localhost to 127.0.0.1 and use TCP
    if host == 'localhost':
        host = '127.0.0.1'
        
    logger.info(f"Attempting connection to {host}:{port} as {user}...")
    
    logger.info(f"Attempting connection to {host}:{port} as {user}...")
    
    # Pre-check: Is the port even open? (Avoids driver hangs/crashes)
    def is_port_open(host, port):
        logger.info(f"Checking TCP port {host}:{port}...")
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("Port is OPEN.")
                return True
        except (socket.timeout, ConnectionRefusedError):
            logger.warning("Port is CLOSED/TIMEOUT.")
            return False
        except Exception as e:
            logger.error(f"Port check error: {e}")
            return False

    if not is_port_open(host, port):
        logger.warning(f"Port {port} on {host} is unreachable.")
        return jsonify({'success': False, 'error': f"Cannot reach {host}:{port}. Is the database running?"}), 400

    def connect_worker():
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=5,
            use_pure=True  # Prevent C-extension crashes
        )
        if conn.is_connected():
            # Extract schema logic
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            schema_info = []
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = [f"{col[0]} ({col[1]})" for col in cursor.fetchall()]
                schema_info.append(f"Table: {table}\nColumns: {', '.join(columns)}")
            
            cursor.close()
            conn.close()
            return "\n\n".join(schema_info)
        return None

    try:
        # Offload connection to thread to prevent blocking main loop
        logger.info("Submitting connection task to thread pool...")
        future = executor.submit(connect_worker)
        # Wait max 10 seconds for the thread
        logger.info("Waiting for thread result (timeout=10s)...")
        result = future.result(timeout=10)
        logger.info(f"Thread returned: {result}")
        
        if result:
            # Save credentials for future queries
            db_config = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'database': database,
                'use_pure': True  # IMPORTANT: Persist this setting for chat queries!
            }
            # Update global schema
            global db_schema
            db_schema = result
            logger.info("Schema fetched successfully")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to connect'}), 400
            
    except concurrent.futures.TimeoutError:
        logger.error("Connection timed out in worker")
        return jsonify({'success': False, 'error': 'Connection timed out (Check Host/Port)'}), 408
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    if not db_config:
        return jsonify({'success': False, 'error': 'Database not connected'}), 400
        
    data = request.json
    user_query = data.get('query')
    
    if not client:
        return jsonify({'success': False, 'error': 'AI Client not initialized'}), 500

    try:
        # 1. Ask AI to generate SQL
        # In a real scenario, you'd feed schema info here. 
        # For now, we simulate the logic from the original app (which looked like it was structured to do RAG or Text-to-SQL)
        
        # NOTE: The original app had logic to "Run Query" but it was commented out or partial.
        # We will implement a basic Text-to-SQL flow here as an example.
        
        # For now, just a simple response to prove connectivity, as schema info retrieval is a larger task.
        # "I received your query: {user_query}. (SQL execution logic to be implemented)"
        
        # Let's try to actually be helpful if we can.
        # Retry logic for API rate limits
        import time
        max_retries = 5
        base_delay = 5
        for attempt in range(max_retries):
            try:
                # Use a specific stable model version if possible, or stick to flash-latest
                chat = client.chats.create(model="gemini-2.5-flash-preview-09-2025")
                
                context = f"""
                You are a MySQL expert. 
                Database Schema:
                {db_schema}
                
                The user asks: '{user_query}'.
                
                If the user asks for a query, provide ONLY the SQL query in a code block (```sql ... ```).
                If the user asks a general question, answer it using the schema context.
                """
                
                response = chat.send_message(context)
                bot_reply = response.text
                
                # Check for SQL code block
                sql_match = re.search(r"```sql\n(.*?)\n```", bot_reply, re.DOTALL)
                if sql_match:
                    sql_query = sql_match.group(1).strip()
                    logger.info(f"Detected SQL: {sql_query}")
                    
                    try:
                        # Execute the generated SQL
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        cursor.execute(sql_query)
                        
                        # Fetch column names and rows
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        rows = cursor.fetchall()
                        
                        cursor.close()
                        conn.close()
                        
                        # Format results for AI to interpret
                        data_summary = f"Columns: {columns}\nRows: {rows}"
                        
                        # Agentic Step: Ask AI to synthesize the answer
                        logger.info(f"Synthesizing answer with data: {data_summary}")
                        
                        followup_prompt = f"""
                        The database returned this data:
                        {data_summary}
                        
                        Based on this data, please answer the user's original question: '{user_query}'.
                        Answer in a friendly, natural language sentence. 
                        Do NOT show the SQL query or the raw data structure in your final response.
                        """
                        
                        final_response = chat.send_message(followup_prompt)
                        bot_reply = final_response.text
                        
                    except Exception as db_err:
                        logger.error(f"SQL Execution Failed: {db_err}")
                        bot_reply = f"I tried to run a query but encountered an error: {str(db_err)}"

                return jsonify({
                    'success': True, 
                    'response': bot_reply,
                    'sql_query': sql_query,
                    'is_sql_query': True,
                    'thought_process': [
                        "Analyzing database schema...",
                        "Identifying relevant tables...",
                        f"Generated SQL: {sql_query[:50]}...",
                        "Executing query against database...",
                        f"Retrieved {len(rows)} rows of data.",
                        "Synthesizing natural language answer..."
                    ]
                })
            except Exception as e:
                # Check for 429 or "RESOURCE_EXHAUSTED"
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # 5, 10, 20, 40...
                    logger.warning(f"Rate limit hit, retrying in {delay} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    raise e

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    try:
        # Run on all interfaces for access, debug mode for development
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.critical(f"Server crashed: {e}", exc_info=True)
        with open("crash_log.txt", "w") as f:
            f.write(str(e))