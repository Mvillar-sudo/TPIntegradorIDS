from flask import Blueprint, jsonify, request
from mysql.connector import Error as MySQLError

try:
    from auth_middleware import token_required
    from validators.medico import validar_id_turno
    from services.medico import listar_turnos_hoy_servicio, marcar_atendido_servicio
except ImportError:
    from backend.auth_middleware import token_required
    from backend.validators.medico import validar_id_turno
    from backend.services.medico import listar_turnos_hoy_servicio, marcar_atendido_servicio

medico_bp = Blueprint("medico", __name__, url_prefix="/api/v1/medicos")

ROLES_MEDICO = ["medico"]


@medico_bp.route("/turnos/hoy", methods=["GET"])
@token_required(roles_permitidos=ROLES_MEDICO)
def ver_turnos_hoy():
    id_usuario = request.user_data.get("id_usuario")
    try:
        respuesta, status_code = listar_turnos_hoy_servicio(id_usuario)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500


@medico_bp.route("/turnos/<id_turno>/atendido", methods=["PATCH"])
@token_required(roles_permitidos=ROLES_MEDICO)
def marcar_atendido(id_turno):
    try:
        id_turno_valido = validar_id_turno(id_turno)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    id_usuario = request.user_data.get("id_usuario")
    try:
        respuesta, status_code = marcar_atendido_servicio(id_usuario, id_turno_valido)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500
