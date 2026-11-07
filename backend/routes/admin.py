from flask import Blueprint, jsonify, request
from mysql.connector import Error

from validators.validator_auth import token_required
from constants import PERSONAL_ROLES, CATALOGO_CAMPOS
from services import admin
from utils import respuesta_error
from validators.admin import validar_catalogo

admin_bp = Blueprint('admin', __name__)


def _validar_recurso(recurso):
    if recurso not in CATALOGO_CAMPOS:
        raise LookupError('El catálogo solicitado no existe')

def _verificar_permisos(roles_permitidos):
    return request.user_data.get('rol_usuario') in roles_permitidos


@admin_bp.route('/<recurso>', methods=['GET'])
@token_required()
def listar_catalogos(recurso):
    try:
        _validar_recurso(recurso)
        
        return jsonify(admin.listar(recurso)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>', methods=['POST'])
@token_required()
def crear_catalogo(recurso):
    try:
        _validar_recurso(recurso)

        if not _verificar_permisos(PERSONAL_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403
        values = validar_catalogo(
            recurso,
            request.get_json(silent=True)
        )

        return jsonify(admin.crear(recurso, values)), 201

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@admin_bp.route('/<recurso>/<int:item_id>', methods=['GET'])
@token_required()
def obtener_catalogo(recurso, item_id):
    try:
        _validar_recurso(recurso)

        return jsonify(admin.obtener(recurso, item_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>/<int:item_id>', methods=['PATCH'])
@token_required()
def actualizar_catalogo(recurso, item_id):
    try:
        _validar_recurso(recurso)

        if not _verificar_permisos(PERSONAL_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403
        values = validar_catalogo(
            recurso,
            request.get_json(silent=True),
            partial=True
        )

        return jsonify(admin.actualizar(recurso, item_id, values)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>/<int:item_id>', methods=['DELETE'])
@token_required()
def eliminar_catalogo(recurso, item_id):
    try:
        _validar_recurso(recurso)

        if not _verificar_permisos(PERSONAL_ROLES):
            return jsonify({'error': 'No posee permisos para esta acción'}), 403
        
        admin.eliminar(recurso, item_id)

        return '', 204

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)