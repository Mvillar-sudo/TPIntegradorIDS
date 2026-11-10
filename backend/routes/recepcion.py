from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError

from validators.validator_auth import token_required
from services.recepcion import obtener_sala_espera

recepcion_bp = Blueprint("recepcion", __name__)


"""
Pre: -
Post: Si el token es válido y pertenece a un rol autorizado ('admin' o 'recepcionista'), devuelve la lista de turnos en sala de espera con código 200. 
En caso de error, devuelve el mensaje y código HTTP correspondiente.
"""
@recepcion_bp.route("/recepcion/sala-espera", methods=["GET"])
def consultar_sala_espera():
    user_data, error_token, codigo = token_required(["admin", "recepcionista"])

    if error_token is not None:
        return jsonify({"error": error_token}), codigo

    try:
        turnos = obtener_sala_espera()
        return jsonify(turnos), 200
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500
