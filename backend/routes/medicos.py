from flask import Blueprint, jsonify, request
from mysql.connector import Error as MySQLError, Error

from validators.validator_auth import token_required
from constants import LECTORES_ROLES, PERSONAL_ROLES
from services import medicos
from utils import respuesta_error, validar_entero_positivo
from validators.medicos import validar_medico, validar_id_turno

medicos_bp = Blueprint('medicos', __name__)

ROLES_MEDICO = ["medico"]


def _verificar_permisos(roles_permitidos):
    return request.user_data.get('rol_usuario') in roles_permitidos


@medicos_bp.route('/medicos', methods=['GET'])
@token_required()
def listar_medicos():
    try:
        if not _verificar_permisos(LECTORES_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403

        raw_specialty = request.args.get('especialidad_id')
        specialty_id = None
        if raw_specialty:
            specialty_id = validar_entero_positivo(raw_specialty, 'especialidad_id')

        return jsonify(medicos.listar(specialty_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@medicos_bp.route('/medicos', methods=['POST'])
@token_required()
def crear_medico():
    try:
        if not _verificar_permisos(PERSONAL_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403

        values = validar_medico(request.get_json(silent=True))
        doctor_id = medicos.crear(values)

        return jsonify({
            'id_medico': doctor_id,
            'mensaje': 'Médico registrado correctamente',
        }), 201

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@medicos_bp.route('/medicos/turnos/hoy', methods=['GET'])
@token_required(roles_permitidos=ROLES_MEDICO)
def ver_turnos_hoy():
    id_usuario = request.user_data.get('id_usuario')
    try:
        respuesta, status_code = medicos.listar_turnos_hoy_servicio(id_usuario)
        return jsonify(respuesta), status_code
    except (MySQLError, Error):
        return jsonify({'error': 'No se pudo conectar a la base de datos o fallo la consulta'}), 500


@medicos_bp.route('/medicos/turnos/<id_turno>/atendido', methods=['PATCH'])
@token_required(roles_permitidos=ROLES_MEDICO)
def marcar_atendido(id_turno):
    try:
        id_turno_valido = validar_id_turno(id_turno)
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    id_usuario = request.user_data.get('id_usuario')
    try:
        respuesta, status_code = medicos.marcar_atendido_servicio(id_usuario, id_turno_valido)
        return jsonify(respuesta), status_code
    except (MySQLError, Error):
        return jsonify({'error': 'No se pudo conectar a la base de datos o fallo la consulta'}), 500


@medicos_bp.route('/medicos/<int:medico_id>', methods=['GET'])
@token_required()
def obtener_medico(medico_id):
    try:
        if not _verificar_permisos(LECTORES_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403

        return jsonify(medicos.obtener(medico_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@medicos_bp.route('/medicos/<int:medico_id>', methods=['PATCH'])
@token_required()
def actualizar_medico(medico_id):
    try:
        if not _verificar_permisos(PERSONAL_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403

        values = validar_medico(
            request.get_json(silent=True),
            partial=True
        )

        return jsonify(medicos.actualizar(medico_id, values)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@medicos_bp.route('/medicos/<int:medico_id>', methods=['DELETE'])
@token_required()
def eliminar_medico(medico_id):
    try:
        if not _verificar_permisos(PERSONAL_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403

        medicos.eliminar(medico_id)

        return '', 204

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)
