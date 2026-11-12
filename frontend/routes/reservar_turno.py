from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from services import reservar_turno


reservar_turno_bp = Blueprint("reservar_turno", __name__)


def _render_reserva(paso=1, especialidad_id="", medicos=None, medico_id="",
                    fecha="", turnos=None, turno=None, error=None,
                    medico_seleccionado=""):
    especialidades, error_carga, _ = reservar_turno.listar_especialidades()
    return render_template(
        "paciente/reservar_turno.html",
        especialidades=especialidades or [],
        error_carga=error_carga,
        error=error,
        reserva=None,
        paso=paso,
        especialidad_id=str(especialidad_id),
        medicos=medicos or [],
        medico_id=str(medico_id),
        fecha=fecha,
        fecha_minima=reservar_turno.fecha_minima(),
        turnos=turnos or [],
        turno=turno,
        medico_seleccionado=medico_seleccionado,
    )


def _contexto_paso_horarios():
    especialidad_id = request.form.get("id_especialidad", "")
    medico_id = request.form.get("medico_id", "")
    fecha = request.form.get("fecha", "")

    try:
        especialidad_id = int(especialidad_id)
        medico_id = int(medico_id)
    except (TypeError, ValueError):
        return None, _render_reserva(error="Seleccioná una especialidad y un médico válidos.")

    medicos, error_medicos, status = reservar_turno.obtener_medicos(especialidad_id)
    if error_medicos:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return None, redirect(url_for("auth.iniciar_sesion"))
        return None, _render_reserva(error=error_medicos)

    medico = next((item for item in medicos if item.get("id_medico") == medico_id), None)
    if medico is None:
        return None, _render_reserva(error="El médico elegido no pertenece a la especialidad.")

    etiqueta_medico = f"{medico.get('nombre_medico', '')} {medico.get('apellido_medico', '')}".strip()
    return {
        "especialidad_id": especialidad_id,
        "medicos": medicos,
        "medico_id": medico_id,
        "fecha": fecha,
        "medico_seleccionado": etiqueta_medico,
    }, None


def _mostrar_paso_horarios(error=None, turnos=None):
    contexto, respuesta = _contexto_paso_horarios()
    if respuesta is not None:
        return respuesta
    return _render_reserva(paso=2, turnos=turnos, error=error, **contexto)


@reservar_turno_bp.before_request
def exigir_paciente():
    if "token" not in session:
        flash("Iniciá sesión como paciente para reservar un turno.", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    if session.get("usuario", {}).get("rol") != "paciente":
        abort(403)


@reservar_turno_bp.route("/reservar_turno", methods=["GET"])
def reservar_pantalla():
    return _render_reserva()


@reservar_turno_bp.route("/reservar_turno/medicos", methods=["POST"])
def obtener_medicos():
    id_especialidad = request.form.get("id_especialidad", type=int)
    if not id_especialidad or id_especialidad < 1:
        return _render_reserva(error="Seleccioná una especialidad válida.")

    medicos, error, status = reservar_turno.obtener_medicos(id_especialidad)
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        return _render_reserva(especialidad_id=id_especialidad, error=error)
    return _render_reserva(especialidad_id=id_especialidad, medicos=medicos)


@reservar_turno_bp.route("/reservar_turno/paso-horarios", methods=["POST"])
def paso_horarios():
    return _mostrar_paso_horarios()


@reservar_turno_bp.route("/reservar_turno/disponibles", methods=["POST"])
def obtener_turnos_disponibles():
    fecha = request.form.get("fecha", "").strip()
    if not reservar_turno.fecha_valida_para_busqueda(fecha):
        return _mostrar_paso_horarios("Elegí una fecha desde mañana en adelante.")

    contexto, respuesta = _contexto_paso_horarios()
    if respuesta is not None:
        return respuesta

    turnos, error, status = reservar_turno.listar_turnos_disponibles(
        contexto["medico_id"],
        contexto["especialidad_id"],
        fecha,
    )
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        return _mostrar_paso_horarios(error)
    disponibles = [turno for turno in (turnos or []) if turno.get("estado") == "disponible"]
    return _mostrar_paso_horarios(turnos=disponibles)


@reservar_turno_bp.route("/reservar_turno/revisar", methods=["POST"])
def revisar_reserva():
    fecha = request.form.get("fecha", "").strip()
    id_turno = request.form.get("id_turno", type=int)
    if not reservar_turno.fecha_valida_para_busqueda(fecha):
        return _mostrar_paso_horarios("Elegí una fecha desde mañana en adelante.")

    contexto, respuesta = _contexto_paso_horarios()
    if respuesta is not None:
        return respuesta

    turnos, error, status = reservar_turno.listar_turnos_disponibles(
        contexto["medico_id"], contexto["especialidad_id"], fecha
    )
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        return _mostrar_paso_horarios(error)

    turno = next((item for item in (turnos or [])
                  if item.get("id_turno") == id_turno and item.get("estado") == "disponible"), None)
    if turno is None:
        return _mostrar_paso_horarios("Ese horario ya no está disponible. Elegí otro.")
    return _render_reserva(paso=3, turno=turno, **contexto)


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