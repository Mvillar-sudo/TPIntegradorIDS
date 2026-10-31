from functools import wraps
import jwt
from flask import jsonify, request

from config import SECRET_KEY

def token_required(roles_permitidos=None):
    """
    Valida el JWT enviado en el header Authorization.
    Opcionalmente, verifica si el rol del usuario está permitido.
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({
                    "error": "Token de autenticación faltante"
                }), 401

            token = auth_header.split(" ", 1)[1]

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                if (roles_permitidos and data.get("rol_usuario") not in roles_permitidos):
                    return jsonify({
                        "error": "No posee permisos para esta acción"
                    }), 403

                request.user_data = data

            except jwt.ExpiredSignatureError:
                return jsonify({
                    "error": "El token ha expirado"
                }) 

            except jwt.InvalidTokenError:
                return jsonify({
                    "error": "Token invalido"
                }), 401

            return f(*args, **kwargs)
        return decorated
    return decorator

def validar_login(datos):
    if not isinstance(datos, dict):
        return False, "Se requiere un objeto JSON válido"

    email = datos.get("email")
    password = datos.get("password")

    if not isinstance(email, str) or not email.strip():
        return False, "El email es obligatorio"

    if not isinstance(password, str) or not password:
        return False, "La contraseña es obligatoria"

    return True, None
