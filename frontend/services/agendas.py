import requests
import os
from flask import session # Asumiendo que guardas el token en la sesión

API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000')

def crear_agenda(datos_formateados):
    url = f"{API_BASE_URL}/api/v1/agendas/generar"
    
    # Recuperamos el token de la sesión del usuario (ajusta esto a cómo manejes tu auth)
    token = session.get('token', '')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    respuesta = requests.post(url, json=datos_formateados, headers=headers)
    respuesta.raise_for_status()
    
    return respuesta.json()