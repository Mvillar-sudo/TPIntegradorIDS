from flask import Blueprint, jsonify, request
from mysql.connector import Error

from ..auth_middleware import token_required
from ..constants import ADMIN_ROLES
from ..services import agendas
from ..utils import respuesta_error
from ..validators.agendas import validar_agenda

agendas_bp = Blueprint('agendas', __name__)


@agendas_bp.route('/agendas', methods=['GET', 'POST'])
@token_required(roles_permitidos=ADMIN_ROLES)
def coleccion_agendas():
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