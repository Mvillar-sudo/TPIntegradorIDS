from flask import Blueprint, jsonify, request
from mysql.connector import Error

from validators.validator_auth import token_required
from utils import respuesta_error
from validators.agendas import validar_agenda
from services import agendas

agendas_bp = Blueprint('agendas', __name__)

@agendas_bp.route('agendas/generar', methods=['POST'])
def generar_agenda():
    # 1. Validar que sea administrador
    '''user_data, error_token, codigo = token_required(["admin"])
    if error_token is not None:
        return jsonify({"error": error_token}), codigo
'''
    try:
        # 2. Validar los datos de entrada (qué médico, qué consultorio, fechas)
        # request.get_json(silent=True) evita que Flask rompa si el JSON viene mal formado
        datos_entrada = request.get_json(silent=True)
        datos_validados = validar_agenda(datos_entrada)

        # 3. Invocar cálculo y guardado a través de la capa de Servicios
        agenda_id, turnos_creados = agendas.crear(datos_validados)

        # 4. Retornar el resultado exitoso
        return jsonify({
            'id_agenda': agenda_id,
            'turnos_generados': turnos_creados,
            'mensaje': 'Agenda configurada y turnos generados correctamente'
        }), 201

    except (ValueError, LookupError, Error) as error:
        # Atrapa los errores de validación, de negocio y de base de datos
        return respuesta_error(error)