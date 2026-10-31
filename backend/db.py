import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="centro_medico"
    )

def execute_query(query, params=None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
            
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Error en execute_query: {e}")
        return None
