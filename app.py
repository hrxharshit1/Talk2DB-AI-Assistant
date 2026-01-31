import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import concurrent.futures
import json

# Import our new modules
import db_helper
import ai_helper

app = Flask(__name__)
CORS(app)

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
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Using defaults.")
        return {}

config = load_config()
API_KEY = config.get("GOOGLE_API_KEY")
GEMINI_MODEL = config.get("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# Initialize AI
ai_helper.init_client(API_KEY, GEMINI_MODEL)

# Global State (Simulated Session)
db_config = {}
db_schema = ""
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

@app.before_request
def log_request():
    logger.info(f"Incoming request: {request.method} {request.url}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/connect', methods=['POST'])
def connect_database():
    data = request.json
    global db_config, db_schema
    
    host = data.get('host')
    if host == 'localhost': host = '127.0.0.1'
    
    port = int(data.get('port', 3306))
    user = data.get('user')
    password = data.get('password')
    database = data.get('database')
    
    logger.info(f"Connecting to {host}:{port}...")

    # Define a helper wrapper for specific args to run in thread
    def connection_task():
        return db_helper.try_connect_db(host, port, user, password, database)

    try:
        # Run connection in background thread
        future = executor.submit(connection_task)
        success, result = future.result(timeout=10)
        
        if success:
            # Store config for later use
            db_config = {
                'host': host, 'port': port, 'user': user,
                'password': password, 'database': database,
                'use_pure': True
            }
            db_schema = result # Result is the schema string
            logger.info("Connected & Schema Fetched.")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result}), 400

    except concurrent.futures.TimeoutError:
        return jsonify({'success': False, 'error': 'Connection timed out'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    if not db_config:
        return jsonify({'success': False, 'error': 'Database not connected'}), 400
        
    data = request.json
    user_query = data.get('query')
    
    # Delegate complex logic to AI Helper
    result = ai_helper.generate_response(user_query, db_schema, db_config)
    
    if result.get("success"):
        return jsonify(result)
    else:
        return jsonify(result), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        logger.critical(f"Server crashed: {e}", exc_info=True)