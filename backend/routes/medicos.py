from flask import Blueprint, jsonify, request
from mysql.connector import Error

from ..auth_middleware import token_required
from ..constants import LECTORES_ROLES, PERSONAL_ROLES
from ..services import medicos
from ..utils import respuesta_error, validar_entero_positivo
from ..validators.medicos import validar_medico

medicos_bp = Blueprint('medicos', __name__)


@medicos_bp.route('/medicos', methods=['GET', 'POST'])
@token_required()
def coleccion_medicos():
    try:
        role = request.user_data.get('rol_usuario')
        if request.method == 'GET':
            if role not in LECTORES_ROLES:
                return jsonify({'error': 'No posee permisos para esta acción'}), 403
            raw_specialty = request.args.get('especialidad_id')
            specialty_id = validar_entero_positivo(raw_specialty, 'especialidad_id') if raw_specialty else None
            return jsonify(medicos.listar(specialty_id)), 200
        if role not in PERSONAL_ROLES:
            return jsonify({'error': 'No posee permisos para esta acción'}), 403
        doctor_id = medicos.crear(validar_medico(request.get_json(silent=True)))
        return jsonify({
            'id_medico': doctor_id,
            'mensaje': 'Médico registrado correctamente',
        }), 201
    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@medicos_bp.route('/medicos/<int:medico_id>', methods=['GET', 'PATCH', 'DELETE'])
@token_required()
def medico_por_item(medico_id):
    role = request.user_data.get('rol_usuario')
    if request.method == 'GET':
        if role not in LECTORES_ROLES:
            return jsonify({'error': 'No posee permisos para esta acción'}), 403
        try:
            return jsonify(medicos.obtener(medico_id)), 200
        except (ValueError, LookupError, Error) as error:
            return respuesta_error(error)

    if role not in PERSONAL_ROLES:
        return jsonify({'error': 'No posee permisos para esta acción'}), 403
    try:
        if request.method == 'PATCH':
            values = validar_medico(request.get_json(silent=True), partial=True)
            return jsonify(medicos.actualizar(medico_id, values)), 200
        medicos.eliminar(medico_id)
        return '', 204
    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)