from functools import wraps
from flask import request, jsonify
import jwt

try:
    from config import SECRET_KEY
except ImportError:
    from backend.config import SECRET_KEY


"""
Pre: roles_permitidos es una lista opcional de strings con los roles autorizados para el endpoint.
Post: Retorna un decorador que valida el JWT del header Authorization e inyecta user_data en request.
"""
def token_required(roles_permitidos=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            auth_header = request.headers.get("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            if not token:
                return jsonify({"error": "Token de autenticación faltante"}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                if roles_permitidos and data.get("rol_usuario") not in roles_permitidos:
                    return jsonify({"error": "No posee permisos para esta acción"}), 403

                request.user_data = data
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "El token ha expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token inválido"}), 401

            return f(*args, **kwargs)

        return decorated

    return decorator
