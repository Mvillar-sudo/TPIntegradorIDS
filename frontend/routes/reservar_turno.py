from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for

from services import reservar_turno


reservar_turno_bp = Blueprint("reservar_turno", __name__)


@reservar_turno_bp.before_request
def exigir_paciente():
    if "token" not in session:
        flash("Iniciá sesión como paciente para reservar un turno.", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    if session.get("usuario", {}).get("rol") != "paciente":
        abort(403)


@reservar_turno_bp.route("/reservar_turno", methods=["GET"])
def reservar_pantalla():
    especialidades, error, status = reservar_turno.listar_especialidades()
    return render_template(
        "paciente/reservar_turno.html",
        especialidades=especialidades or [],
        error_carga=error,
        reserva=None,
    ), (status if error and status not in (0, 401) else 200)


@reservar_turno_bp.route("/reservar_turno/api/medicos", methods=["GET"])
def obtener_medicos():
    id_especialidad = request.args.get("id_especialidad", type=int)
    if not id_especialidad or id_especialidad < 1:
        return jsonify({"error": "Seleccioná una especialidad válida."}), 400

    medicos, error, status = reservar_turno.listar_medicos(id_especialidad)
    if error:
        return jsonify({"error": error}), status if status else 502
    return jsonify(medicos or [])


@reservar_turno_bp.route("/reservar_turno/api/disponibles", methods=["GET"])
def obtener_turnos_disponibles():
    medico_id = request.args.get("medico_id", type=int)
    id_especialidad = request.args.get("id_especialidad", type=int)
    fecha = request.args.get("fecha", "").strip()

    if not medico_id or not id_especialidad or not fecha:
        return jsonify({"error": "Indicá especialidad, médico y fecha."}), 400

    turnos, error, status = reservar_turno.listar_turnos_disponibles(
        medico_id, id_especialidad, fecha
    )
    if error:
        return jsonify({"error": error}), status if status else 502
    return jsonify(turnos or [])


@reservar_turno_bp.route("/reservar_turno/reservar", methods=["POST"])
def confirmar_reserva():
    id_turno = request.form.get("id_turno", type=int)
    if not id_turno or id_turno < 1:
        flash("Elegí un horario antes de confirmar.", "error")
        return redirect(url_for("reservar_turno.reservar_pantalla"))

    reserva, error, status = reservar_turno.reservar_turno(id_turno)
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        flash(error, "error")
        return redirect(url_for("reservar_turno.reservar_pantalla"))

    especialidades, _, _ = reservar_turno.listar_especialidades()
    detalle_turno = {
        "id_turno": request.form.get("detalle_id_turno") or id_turno,
        "especialidad": request.form.get("detalle_especialidad", "").strip(),
        "medico": request.form.get("detalle_medico", "").strip(),
        "consultorio": request.form.get("detalle_consultorio", "").strip(),
        "fecha_hora": request.form.get("detalle_fecha_hora", "").strip(),
    }

    return render_template(
        "paciente/reservar_turno.html",
        especialidades=especialidades or [],
        error_carga=None,
        reserva=reserva,
        detalle_turno=detalle_turno,
    )