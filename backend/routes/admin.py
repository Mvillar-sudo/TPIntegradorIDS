from flask import Blueprint, jsonify, request
from mysql.connector import Error

from ..auth_middleware import token_required
from ..constants import PERSONAL_ROLES, CATALOGO_CAMPOS
from ..services import admin
from ..utils import respuesta_error
from ..validators.admin import validar_catalogo

admin_bp = Blueprint('admin', __name__)


def _validar_recurso(resource):
	if resource not in CATALOGO_CAMPOS:
		raise LookupError('El catálogo solicitado no existe')


@admin_bp.route('/<resource>', methods=['GET', 'POST'])
@token_required()
def coleccion_catalogos(resource):
	try:
		_validar_recurso(resource)
		if request.method == 'GET':
			return jsonify(admin.listar(resource)), 200
		if request.user_data.get('rol_usuario') not in PERSONAL_ROLES:
			return jsonify({'error': 'No posee permisos para esta acción'}), 403
		values = validar_catalogo(resource, request.get_json(silent=True))
		return jsonify(admin.crear(resource, values)), 201
	except (ValueError, LookupError, Error) as error:
		return respuesta_error(error)


@admin_bp.route('/<resource>/<int:item_id>', methods=['GET', 'PATCH', 'DELETE'])
@token_required()
def catalaogo_por_item(resource, item_id):
	try:
		_validar_recurso(resource)
		if request.method == 'GET':
			return jsonify(admin.obtener(resource, item_id)), 200
		if request.user_data.get('rol_usuario') not in PERSONAL_ROLES:
			return jsonify({'error': 'No posee permisos para esta acción'}), 403
		if request.method == 'PATCH':
			values = validar_catalogo(resource, request.get_json(silent=True), partial=True)
			return jsonify(admin.actualizar(resource, item_id, values)), 200
		admin.eliminar(resource, item_id)
		return '', 204
	except (ValueError, LookupError, Error) as error:
		return respuesta_error(error)