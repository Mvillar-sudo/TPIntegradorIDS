import jwt

from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY
from validators.validator_auth import token_required, validar_login
from repositories.usuarios_repositories import obtener_usuario_por_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=['POST'])
def crear_paciente():
    pass

@auth_bp.route("/auth/login", methods=['POST'])
def login():
    datos = request.get_json(silent=True)
    valido, error = validar_login(datos)

    if not valido:
        return jsonify({
            "error": error
        }), 400

    email = datos["email"].strip().lower()
    password = datos["password"]
    usuario = obtener_usuario_por_email(email)

    if not usuario or not check_password_hash(usuario["password_hash"], password):
        return jsonify({
            "error": "Email o contraseña incorrectos"
        }), 401

    ahora = datetime.now(timezone.utc)

    payload = {
        "id_usuario": usuario["id_usuario"],
        "rol_usuario": usuario["rol_usuario"],
        "iat": ahora, # iat : Issued AT
        "exp": ahora + timedelta(hours=2) # exp : Expiration Time 
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "token": token,
        "token_type": "Bearer",
        "expires_in": 7200,
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre_usuario"],
            "apellido": usuario["apellido_usuario"],
            "email": usuario["email_usuario"],
            "rol": usuario["rol_usuario"]
        }
    }), 200