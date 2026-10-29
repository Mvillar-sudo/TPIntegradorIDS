import jwt
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'clave_secreta_jwt_salud_integral'

def token_required(roles_permitidos=None):
    """
    Decorador para validar el JWT enviado en el header Authorization.
    Opcionalmente verifica si el id_rol del usuario esta dentro de roles_permitidos.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            if not token:
                return jsonify({"error": "Token de autenticación faltante"}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                # Se valida el rol del usuario si el endpoint lo requiere
                if roles_permitidos and data.get("id_rol") not in roles_permitidos:
                    return jsonify({"error": "No posee permisos para esta acción"}), 403
                
                # Se inyecta la información del usuario autenticado en la petición
                request.user_data = data
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "El token ha expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token inválido"}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator
