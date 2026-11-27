from flask import Blueprint, jsonify, request
from mysql.connector import Error

from validators.validator_auth import token_required
from constants import CATALOGO_CAMPOS
from services import admin
from utils import respuesta_error
from validators.admin import validar_catalogo

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
def validar_recurso_pedido():
    """
    Pre: -
    Post: Si la ruta tiene un <recurso> que no es un catálogo (por ejemplo /cualquiera), responde
          404 antes de pedir el token. Así una ruta que no existe da 404 y no 401.
    """
    recurso = (request.view_args or {}).get('recurso')

    if recurso is not None and recurso not in CATALOGO_CAMPOS:
        return respuesta_error(LookupError('El catálogo solicitado no existe'))


@admin_bp.route('/<recurso>', methods=['GET'])
def listar_catalogos(recurso):

    _, error_token, codigo = token_required(["admin"])
    
    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        return jsonify(admin.listar(recurso)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>', methods=['POST'])
def crear_catalogo(recurso):


    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        values = validar_catalogo(
            recurso,
            request.get_json(silent=True)
        )

        return jsonify(admin.crear(recurso, values)), 201

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@admin_bp.route('/<recurso>/<int:item_id>', methods=['GET'])
def obtener_catalogo(recurso, item_id):

    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        return jsonify(admin.obtener(recurso, item_id)), 200

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)


@admin_bp.route('/<recurso>/<int:item_id>', methods=['PATCH'])
def actualizar_catalogo(recurso, item_id):
    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
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

    _, error_token, codigo = token_required(["admin"])
    
    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        admin.eliminar(recurso, item_id)

        return '', 204

    except (ValueError, LookupError, Error) as error:
        return respuesta_error(error)

@admin_bp.route('/admin/resumen', methods=['GET'])
def obtener_resumen():

    _, error_token, codigo = token_required(["admin"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        return jsonify(admin.resumen()), 200

    except Error as error:
        return respuesta_error(error)