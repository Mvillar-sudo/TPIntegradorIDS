from flask import Blueprint, jsonify, request
from mysql.connector import Error

from services.estadisticas import obtener_estadisticas
from validators.estadisticas import validar_filtros_estadisticas
from validators.validator_auth import token_required
from services.checkin_qr import marcar_ausentes
estadisticas_bp = Blueprint('estadisticas', __name__)


@estadisticas_bp.route('/estadisticas', methods=['GET'])
def consultar_estadisticas():
    user_data, error_token, codigo = token_required(['admin'])
    if error_token is not None:
        return jsonify({'error': error_token}), codigo

    try:
        desde, hasta = validar_filtros_estadisticas(request.args)
        marcar_ausentes()
        return jsonify(obtener_estadisticas(desde, hasta)), 200
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    except Error:
        return jsonify({'error': 'No se pudo conectar a la base de datos o fallo la consulta'}), 500