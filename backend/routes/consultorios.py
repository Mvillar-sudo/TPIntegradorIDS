from flask import Blueprint, jsonify
from mysql.connector import Error

from constants import GESTION_ROLES
from services import admin
from utils import respuesta_error
from validators.validator_auth import token_required

consultorios_bp = Blueprint('consultorios', __name__)


@consultorios_bp.route('/consultorios', methods=['GET'])
def listar_consultorios():

    _, error_token, codigo = token_required(GESTION_ROLES)

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        return jsonify(admin.listar('consultorios')), 200

    except Error as error:
        return respuesta_error(error)
