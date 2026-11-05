from flask import (Blueprint, jsonify, request, render_template, url_for, flash, redirect)
from mysql.connector import Error as MySQLError

from services.medico import (obtener_perfil_medico, obtener_turnos_hoy, registrar_turno_atendido)

from validators.validator_auth import token_required
from validators.medico import validar_id_turno
from services.medico import (listar_turnos_hoy_servicio, marcar_atendido_servicio)

medico_bp = Blueprint("medico", __name__)


"""
Pre: -
Post: Renderiza la plantilla 'medico.html' con la información del médico y la lista de turnos asignados.
"""
@medico_bp.route('/medico', methods=['GET'])
def agenda():
    perfil = obtener_perfil_medico()
    turnos = obtener_turnos_hoy()
    return render_template('medico.html', medico=perfil, turnos=turnos)

"""
Pre: 'id_turno' es un entero positivo que identifica al turno a atender.
Post: Registra el turno como atendido y redirige a la agenda limpia evitando reenvío de formularios.
"""
@medico_bp.route('/medico/turnos/<int:id_turno>/atender', methods=['POST'])
def atender_turno(id_turno):
    try:
        resultado = registrar_turno_atendido(id_turno)
        flash(f'Consulta finalizada con éxito. Turno #{id_turno} marcado como atendido.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('medico.agenda'))


@medico_bp.route("/turnos/hoy", methods=["GET"])
def ver_turnos_hoy():

    user_data, error_token, codigo = token_required(["admin", "medico"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    id_usuario = user_data["id_usuario"]
    try:
        respuesta, status_code = listar_turnos_hoy_servicio(id_usuario)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500


@medico_bp.route("/turnos/<id_turno>/atendido", methods=["PATCH"])
def marcar_atendido(id_turno):

    user_data, error_token, codigo = token_required(["admin", "medico"])

    if error_token is not None:
        return jsonify({
            "error": error_token
        }), codigo

    try:
        id_turno_valido = validar_id_turno(id_turno)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    id_usuario = user_data["id_usuario"]
    try:
        respuesta, status_code = marcar_atendido_servicio(id_usuario, id_turno_valido)
        return jsonify(respuesta), status_code
    except MySQLError:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500
