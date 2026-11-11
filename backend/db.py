import mysql.connector

from config import obtener_configuracion_db


def get_connection():
    return mysql.connector.connect(**obtener_configuracion_db())
