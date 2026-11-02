import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host = os.getenv("DB_HOST", "localhost"),
        port = int(os.getenv("DB_PORT", "3306")),
        database = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD")
    )

