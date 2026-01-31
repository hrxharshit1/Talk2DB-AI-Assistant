from google import genai
import logging
import re
import time
import mysql.connector

logger = logging.getLogger(__name__)

# Initialize Client
client = None
model_name = "gemini-2.0-flash" # Default

def init_client(api_key, model="gemini-2.0-flash"):
    global client, model_name
    try:
        client = genai.Client(api_key=api_key)
        model_name = model
        return True
    except Exception as e:
        logger.error(f"AI Init Error: {e}")
        return False

def generate_response(query, db_schema, db_config):
    """
    1. Ask AI for SQL
    2. Run SQL
    3. Ask AI to summarize answer
    """
    if not client:
        return {"success": False, "error": "AI Client not ready"}

    steps = []
    steps.append("Analyzing database schema...")
    
    # 1. Generate SQL
    steps.append("Identifying relevant tables...")
    try:
        # Define models to try in order
        models_to_try = [model_name, "gemini-flash-latest"]
        # If the primary model is already gemini-flash-latest, don't duplicate it in the list efficiently
        if model_name == "gemini-flash-latest":
            models_to_try = ["gemini-flash-latest"]
            
        final_exception = None
        
        for current_model in models_to_try:
            try:
                logger.info(f"Attempting to generate response with model: {current_model}")
                chat = client.chats.create(model=current_model)
                
                context = f"""
                You are a MySQL expert. 
                Database Schema:
                {db_schema}
                
                The user asks: '{query}'.
                
                If the user asks for a query, provide ONLY the SQL query in a code block (```sql ... ```).
                If the user asks a general question, answer it using the schema context.
                """
                
                response = chat.send_message(context)
                bot_reply = response.text
                
                # Check for SQL
                sql_match = re.search(r"```sql\n(.*?)\n```", bot_reply, re.DOTALL)
                
                if sql_match:
                    sql_query = sql_match.group(1).strip()
                    steps.append(f"Generated SQL ({current_model}): {sql_query[:50]}...")
                    
                    # 2. Execute SQL
                    steps.append("Executing query against database...")
                    try:
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        cursor.execute(sql_query)
                        
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        rows = cursor.fetchall()
                        
                        cursor.close()
                        conn.close()
                        
                        steps.append(f"Retrieved {len(rows)} rows of data.")
                        
                        # 3. Synthesize Answer
                        steps.append("Synthesizing natural language answer...")
                        data_summary = f"Columns: {columns}\nRows: {rows}"
                        
                        followup_prompt = f"""
                        The database returned this data:
                        {data_summary}
                        
                        Based on this data, please answer the user's original question: '{query}'.
                        Answer in a friendly, natural language sentence. 
                        Do NOT show the SQL query or the raw data structure in your final response.
                        """
                        
                        final_response = chat.send_message(followup_prompt)
                        return {
                            "success": True,
                            "response": final_response.text,
                            "sql_query": sql_query,
                            "is_sql_query": True,
                            "thought_process": steps
                        }
                        
                    except Exception as db_err:
                        return {
                            "success": True, # Still a valid AI interaction, just a DB error response
                            "response": f"I tried to run a query but encountered an error: {str(db_err)}",
                            "sql_query": sql_query,
                            "is_sql_query": True,
                            "thought_process": steps + [f"Error executing SQL: {db_err}"]
                        }
                else:
                    # General Chat (No SQL)
                    return {
                        "success": True,
                        "response": bot_reply,
                        "is_sql_query": False,
                        "thought_process": ["Analyzed query.", f"Generated direct response with {current_model}."]
                    }
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"Rate limit hit for {current_model}. Trying next model...")
                    steps.append(f"Rate limit hit for {current_model}. Switching backup model...")
                    final_exception = e
                    continue # Try next model
                else:
                    raise e # Re-raise if it's not a rate limit issue
        
        # If we get here, all models failed
        if final_exception:
            raise final_exception
            
    except Exception as e:
        logger.error(f"AI Generation Error: {e}")
        return {"success": False, "error": str(e)}
