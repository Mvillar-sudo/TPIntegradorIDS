from flask import Blueprint, flash, redirect, render_template, session, url_for
from services.medico import (
    obtener_perfil_medico,
    obtener_turnos_y_medico_hoy,
    obtener_turnos_semana,
    registrar_turno_atendido,
)

from services.sesion import exigir_rol

medico_bp = Blueprint("medico", __name__)


"""
Pre: -
Post: Redirige al login si no hay sesión iniciada, o muestra el acceso denegado (403) si el usuario
      no tiene rol de médico.
"""
@medico_bp.before_request
def exigir_medico():
    return exigir_rol(("medico",))


"""
Pre: -
Post: Renderiza la plantilla "medico.html" con la información del médico y la lista de turnos asignados desde la API.
"""
@medico_bp.route("/medico", methods=["GET"])
def agenda():
    turnos, id_medico, error, status = obtener_turnos_y_medico_hoy()
    if status == 401:
        session.clear()
        flash("Tu sesión expiró, iniciá sesión nuevamente.", "danger")
        return redirect(url_for("auth.iniciar_sesion"))

    perfil = obtener_perfil_medico(id_medico)

    if error:
        flash(error, "danger")

    return render_template("medico.html", medico=perfil, turnos=turnos)


"""
Pre: "id_turno" es un entero positivo que identifica al turno a atender.
Post: Registra el turno como atendido en el backend y redirige a la agenda.
"""
@medico_bp.route("/medico/turnos/<int:id_turno>/atender", methods=["POST"])
def atender_turno(id_turno):
    datos, error, status = registrar_turno_atendido(id_turno)
    if status == 401:
        session.clear()
        flash("Tu sesión expiró, iniciá sesión nuevamente.", "danger")
        return redirect(url_for("auth.iniciar_sesion"))

    if error:
        flash(error, "danger")
    else:
        flash(f"Consulta finalizada con éxito. Turno #{id_turno} marcado como atendido.", "success")

    return redirect(url_for("medico.agenda"))

"""
Pre: -
Post: Renderiza 'medico_semana.html' con los turnos del médico de los próximos 7 días agrupados por día.
"""
@medico_bp.route("/medico/semana", methods=["GET"])
def agenda_semana():
    dias, error, status = obtener_turnos_semana()
    if status == 401:
        session.clear()
        flash("Tu sesión expiró, iniciá sesión nuevamente.", "danger")
        return redirect(url_for("auth.iniciar_sesion"))

    if error:
        flash(error, "danger")

    return render_template("medico_semana.html", dias=dias)
