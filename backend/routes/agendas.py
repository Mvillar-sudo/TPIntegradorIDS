from flask import Blueprint, jsonify, request
from mysql.connector import Error

from validators.validator_auth import token_required
from services import agendas
from utils import respuesta_error
from validators.agendas import validar_agenda

agendas_bp = Blueprint('agendas', __name__)


@agendas_bp.route('/agendas', methods=['GET', 'POST'])
def coleccion_agendas():

    user_data, error_token, codigo = token_required(["admin", "recepcionista"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo


    try:
        if request.method == 'GET':
            return jsonify(agendas.listar()), 200
        
        agenda_id, created_count = agendas.crear(validar_agenda(request.get_json(silent=True)))

        return jsonify({
            'id_agenda': agenda_id,
            'turnos_generados': created_count,
            'mensaje': 'Agenda configurada y turnos generados correctamente',
        }), 201

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@agendas_bp.route('/agendas/<int:agenda_id>', methods=['DELETE'])
def eliminar_agenda(agenda_id):

    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        agendas.eliminar(agenda_id)

        return '', 204

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)