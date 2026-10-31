from flask import Blueprint, jsonify, request
from mysql.connector import Error as MySQLError

try:
    from auth_middleware import token_required
    from validators.checkin_qr import validar_entrada_checkin
    from services.checkin_qr import registrar_checkin_por_qr
except ImportError:
    from backend.auth_middleware import token_required
    from backend.validators.checkin_qr import validar_entrada_checkin
    from backend.services.checkin_qr import registrar_checkin_por_qr

checkin_qr_bp = Blueprint("checkin_qr", __name__, url_prefix="/api/v1")

ROLES_RECEPCION = ["admin", "recepcionista"]

@checkin_qr_bp.route("/turnos/checkin", methods=["POST"])
@token_required(roles_permitidos=ROLES_RECEPCION)
def checkin_turno():
    try:
        datos_body = request.get_json(silent=True)
        codigo_qr_hash = validar_entrada_checkin(datos_body)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    try:
        respuesta, status_code = registrar_checkin_por_qr(codigo_qr_hash)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500