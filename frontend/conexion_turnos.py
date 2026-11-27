from flask import redirect, url_for, flash
import requests

BACKEND_URL = 'http://127.0.0'
TOKEN_SIMULADO = 'a1b2c3d4e5_token_de_prueba'

def procesar_cancelacion_frontend(id_turno):
    url = f"{BACKEND_URL}/{id_turno}/cancelar"
    headers = {
        "Authorization": f"Bearer {TOKEN_SIMULADO}"
    }
    
    try:
        respuesta = requests.post(url, headers=headers)
        datos = respuesta.json()
        
        if respuesta.status_code == 200:
            flash(datos.get("mensaje"), "success")
        else:
            flash(datos.get("error"), "error")
            
    except requests.exceptions.RequestException:
        flash("No se pudo conectar con el servidor de Backend", "error")
        
    return redirect(url_for('mis_turnos_route'))
