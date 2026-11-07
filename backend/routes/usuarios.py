from flask import Blueprint, jsonify, request

from constants import ADMIN_ROLES
from services.usuarios import registrar_usuario
from validators.usuarios import validar_rol_personal
from validators.validator_auth import token_required

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios", methods=["POST"])
def crear_usuario_personal():

    data_usuario, error_token, codigo = token_required(ADMIN_ROLES)

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    datos = request.get_json(silent=True)

    rol, error = validar_rol_personal(datos)
    if error is not None:
        return jsonify({"error": error}), 400

    usuario, error, codigo = registrar_usuario(datos, rol)
    if error is not None:
        return jsonify({"error": error}), codigo

    return jsonify({
        "mensaje": "Usuario registrado correctamente",
        "usuario": usuario
    }), 201
