import mysql.connector
import socket
import logging

# Configure Logging (re-use same logger setup or simple print for now)
logger = logging.getLogger(__name__)

def is_port_open(host, port):
    """Checks if the database port is reachable."""
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except:
        return False

def get_schema_info_from_conn(conn):
    """Extracts table and column info from a live connection."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    
    schema_info = []
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        columns = [f"{col[0]} ({col[1]})" for col in cursor.fetchall()]
        schema_info.append(f"Table: {table}\nColumns: {', '.join(columns)}")
    
    cursor.close()
    return "\n\n".join(schema_info)

def try_connect_db(host, port, user, password, database):
    """Attempts to connect and returns (success, result_or_error)."""
    
    # 1. Port Check
    if not is_port_open(host, port):
        return False, f"Port {port} on {host} is unreachable."

    # 2. Connection
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=5,
            use_pure=True
        )
        
        if conn.is_connected():
            schema = get_schema_info_from_conn(conn)
            conn.close()
            return True, schema
        else:
            return False, "Failed to establish connection."
            
    except Exception as e:
        return False, str(e)
