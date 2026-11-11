from flask import Blueprint, jsonify, request
from mysql.connector import Error

from validators.validator_auth import token_required
from validators.medicos import validar_medico

from services import medicos

from constants import GESTION_ROLES, LECTORES_ROLES
from utils import respuesta_error, validar_entero_positivo

medicos_bp = Blueprint('medicos', __name__)


@medicos_bp.route('/medicos', methods=['GET'])
def listar_medicos():

    _, error_token, codigo = token_required(LECTORES_ROLES)

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo
    
    try:    
        raw_specialty = request.args.get('id_especialidad')
        specialty_id = None
        if raw_specialty:
            specialty_id = validar_entero_positivo(raw_specialty, 'id_especialidad')

        return jsonify(medicos.listar(specialty_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@medicos_bp.route('/medicos', methods=['POST'])
def crear_medico():
  
    _, error_token, codigo = token_required(GESTION_ROLES)

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:

        values = validar_medico(request.get_json(silent=True))
        doctor_id = medicos.crear(values)

        return jsonify({
            'id_medico': doctor_id,
            'mensaje': 'Médico registrado correctamente',
        }), 201

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@medicos_bp.route('/medicos/<int:medico_id>', methods=['GET'])
def obtener_medico(medico_id):

    _, error_token, codigo = token_required(LECTORES_ROLES)

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        return jsonify(medicos.obtener(medico_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@medicos_bp.route('/medicos/<int:medico_id>', methods=['PATCH'])
def actualizar_medico(medico_id):

    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        values = validar_medico(
            request.get_json(silent=True),
            partial=True
        )

        return jsonify(medicos.actualizar(medico_id, values)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@medicos_bp.route('/medicos/<int:medico_id>', methods=['DELETE'])
def eliminar_medico(medico_id):

    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        medicos.eliminar(medico_id)

        return '', 204

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)