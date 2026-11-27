from flask import Blueprint, jsonify

from repositories.especialidades_repositories import obtener_especialidades
from validators.validator_auth import token_required

especialidades_bp = Blueprint('especialidades', __name__)


@especialidades_bp.route("/especialidades", methods=["GET"])
def listar_especialidades():

    data_usuario, error_token, codigo = token_required()

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    resultados = obtener_especialidades()

    if resultados is None:
        return jsonify({
            "error": "No se pudieron obtener las especialidades."
        }), 500

    especialidades = [
        {
            "id_especialidad": row["id_especialidad"],
            "nombre": row["nombre_especialidad"]
        }
        for row in resultados
    ]

    return jsonify(especialidades), 200
