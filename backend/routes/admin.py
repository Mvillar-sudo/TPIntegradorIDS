from flask import Blueprint, jsonify, request
from mysql.connector import Error

from validators.validator_auth import token_required
from ..constants import PERSONAL_ROLES, CATALOGO_CAMPOS
from ..services import admin
from ..utils import respuesta_error
from ..validators.admin import validar_catalogo

admin_bp = Blueprint('admin', __name__)


def _validar_recurso(recurso):
    if recurso not in CATALOGO_CAMPOS:
        raise LookupError('El catálogo solicitado no existe')


@admin_bp.route('/<recurso>', methods=['GET'])
def listar_catalogos(recurso):

    user_data, error_token, codigo = token_required(["admin"])
    if error_token:
        return jsonify({
            "error": error_token
        }), codigo
    

    try:
        _validar_recurso(recurso)
        
        return jsonify(admin.listar(recurso)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>', methods=['POST'])
def crear_catalogo(recurso):
    try:
        _validar_recurso(recurso)

        user_data, error_token, codigo = token_required(["admin"])
        if error_token:
            return jsonify({
                "error": error_token
            }), codigo

        
        values = validar_catalogo(
            recurso,
            request.get_json(silent=True)
        )

        return jsonify(admin.crear(recurso, values)), 201

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@admin_bp.route('/<recurso>/<int:item_id>', methods=['GET'])
def obtener_catalogo(recurso, item_id):

    user_data, error_token, codigo = token_required(["admin"])
    if error_token:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        _validar_recurso(recurso)

        return jsonify(admin.obtener(recurso, item_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>/<int:item_id>', methods=['PATCH'])
def actualizar_catalogo(recurso, item_id):

    user_data, error_token, codigo = token_required(["admin"])
    if error_token:
        return jsonify({
            "error": error_token
        }), codigo


    try:
        _validar_recurso(recurso)
        values = validar_catalogo(
            recurso,
            request.get_json(silent=True),
            partial=True
        )

        return jsonify(admin.actualizar(recurso, item_id, values)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>/<int:item_id>', methods=['DELETE'])
def eliminar_catalogo(recurso, item_id):

    user_data, error_token, codigo = token_required(["admin"])
    if error_token:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        _validar_recurso(recurso)
        
        admin.eliminar(recurso, item_id)

        return '', 204

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)