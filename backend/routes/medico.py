from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError

from validators.validator_auth import token_required
from validators.medico import validar_id_turno
from services.medico import (listar_turnos_hoy_servicio, marcar_atendido_servicio)

medico_bp = Blueprint("medico", __name__)


@medico_bp.route("/medicos/turnos/hoy", methods=["GET"])
def ver_turnos_hoy():

    user_data, error_token, codigo = token_required(["admin", "medico"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    id_usuario = user_data["id_usuario"]
    try:
        respuesta, status_code = listar_turnos_hoy_servicio(id_usuario)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500


@medico_bp.route("/medicos/turnos/<id_turno>/atendido", methods=["PATCH"])
def marcar_atendido(id_turno):

    user_data, error_token, codigo = token_required(["admin", "medico"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        id_turno_valido = validar_id_turno(id_turno)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    id_usuario = user_data["id_usuario"]
    try:
        respuesta, status_code = marcar_atendido_servicio(id_usuario, id_turno_valido)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500
     
    
