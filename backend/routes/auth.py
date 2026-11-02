import jwt

from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY
from validators.validator_auth import token_required, validar_login, validar_registro
from repositories.usuarios_repositories import (
    obtener_usuario_por_email, obtener_usuario_por_dni, crear_usuario
)
from mysql.connector import Error, IntegrityError, errorcode

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=['POST'])
def crear_paciente():
    datos = request.get_json(silent=True)

    valido, error = validar_registro(datos)
    if not valido:
        return jsonify({"error": error}), 400

    nombre = datos["nombre"].strip()
    apellido = datos["apellido"].strip()
    dni = datos["dni"].strip()
    email = datos["email"].strip().lower()
    telefono = (datos.get("telefono") or "").strip() or None
    id_cobertura = datos.get("id_cobertura")

    try:
        if obtener_usuario_por_email(email):
            return jsonify({"error": "El email ya está registrado"}), 409

        if obtener_usuario_por_dni(dni):
            return jsonify({"error": "El DNI ya está registrado"}), 409

        password_hash = generate_password_hash(datos["password"])

        id_usuario = crear_usuario(
            nombre, apellido, dni, email, password_hash, telefono, id_cobertura
        )

    except IntegrityError as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": "El email o el DNI ya están registrados"}), 409
        if err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            return jsonify({"error": "La cobertura indicada no existe"}), 400
        return jsonify({"error": "No se pudo registrar el usuario"}), 500

    except Error:
        return jsonify({"error": "No se pudo registrar el usuario"}), 500

    return jsonify({
        "mensaje": "Usuario registrado correctamente",
        "usuario": {
            "id_usuario": id_usuario, "nombre": nombre, "apellido": apellido,
            "email": email, "rol": "paciente"
        }
    }), 201

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