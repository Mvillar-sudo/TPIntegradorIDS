import requests
import os
from flask import session 

def obtener_medicos():
    
    url = f"{API_BASE_URL}/api/v1/medicos" 
    

    token = session.get('token', '')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    
    respuesta = requests.get(url, headers=headers)
    
    
    respuesta.raise_for_status()
    
   
    return respuesta.json()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5001')

def crear_agenda(datos_formateados):
    url = f"{API_BASE_URL}/api/v1/agendas/generar"
    token = session.get('token', '')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    respuesta = requests.post(url, json=datos_formateados, headers=headers)
    respuesta.raise_for_status()
    
    return respuesta.json()