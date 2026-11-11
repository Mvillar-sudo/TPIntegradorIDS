from flask import Blueprint, jsonify, request
from mysql.connector import Error as MySQLError


from validators.validator_auth import token_required
from validators.checkin_qr import validar_entrada_checkin
from services.checkin_qr import registrar_checkin_por_qr


checkin_qr_bp = Blueprint("checkin_qr", __name__)


@checkin_qr_bp.route("/turnos/checkin", methods=["POST"])
def checkin_turno():

    user_data, error_token, codigo = token_required(["admin", "recepcionista"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        datos_body = request.get_json(silent=True)
        token_qr = validar_entrada_checkin(datos_body)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    try:
        respuesta, status_code = registrar_checkin_por_qr(token_qr)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500