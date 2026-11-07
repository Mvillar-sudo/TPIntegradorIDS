import requests
from flask import session
from constants import BACKEND_URL

SIN_CONEXION = 0


def pedir(metodo, ruta, json=None, params=None):
    """Llama al backend con el token de la sesión.

    Devuelve (datos, error, status):
      - ok:             (datos, None, status)
      - error backend:  (None, mensaje, status)   # status 401 = token vencido
      - sin conexión:   (None, mensaje, SIN_CONEXION)
    """
    headers = {"Authorization": f"Bearer {session.get('token', '')}"}

    try:
        r = requests.request(
            metodo, f"{BACKEND_URL}{ruta}",
            json=json, params=params, headers=headers, timeout=5
        )
    except requests.exceptions.RequestException:
        return None, "No se pudo conectar con el servidor", SIN_CONEXION

    try:
        datos = r.json() if r.content else None
    except ValueError:
        datos = None

    if not r.ok:
        mensaje = datos.get("error") if isinstance(datos, dict) else None
        return None, mensaje or "Error en el servidor", r.status_code

    return datos, None, r.status_code
