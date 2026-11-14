from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from services.reservar_turno import render_reserva, listar_medicos, listar_especialidades, mostrar_paso_horarios, fecha_valida_para_busqueda, contexto_paso_horarios, listar_turnos_disponibles, reservar_turno


reservar_turno_bp = Blueprint("reservar_turno", __name__)


def exigir_paciente():
    """
    - si el usuario no esta autenticado, se redirige a iniciar sesion
    - si el usuario autenticado no es paciente se lanza error 403 (El usuario no tiene permisos)
    - si todo sale bien se devuelve vacio
    """
    if "token" not in session:
        flash("Iniciá sesión como paciente para reservar un turno.", "error")
        return redirect(url_for("auth.iniciar_sesion"))

    if session.get("usuario", {}).get("rol") != "paciente":
        abort(403)
    return None


@reservar_turno_bp.route("/reservar_turno", methods=["GET"])
def reservar_pantalla():
    """
    renderiza reservar_turno.html
    """
    bloqueo = exigir_paciente()
    if bloqueo:
        return bloqueo
    
    return render_reserva()


@reservar_turno_bp.route("/reservar_turno/medicos", methods=["POST"])
def obtener_medicos():
    """
    sin errores se devuelve lista de medicos de id_especialidad
    """

    bloqueo = exigir_paciente()
    if bloqueo:
        return bloqueo
    
    id_especialidad = request.form.get("id_especialidad", type=int)
    if not id_especialidad or id_especialidad < 1:
        return render_reserva(error="Seleccioná una especialidad válida.")

    medicos, error, status = listar_medicos(id_especialidad)
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        return render_reserva(especialidad_id=id_especialidad, error=error)
    return render_reserva(especialidad_id=id_especialidad, medicos=medicos)


@reservar_turno_bp.route("/reservar_turno/paso-horarios", methods=["POST"])
def paso_horarios():
    """
    devuelve horarios de turnos disponibles
    """
    bloqueo = exigir_paciente()
    if bloqueo:
        return bloqueo
    return mostrar_paso_horarios()


@reservar_turno_bp.route("/reservar_turno/disponibles", methods=["POST"])
def obtener_turnos_disponibles():
    """
    sin errores se renderiza de nuevo reservar_turno.html en el paso 2 con los datos de turnos disponibles
    """
    bloqueo = exigir_paciente()
    if bloqueo:
        return bloqueo

    fecha = request.form.get("fecha", "").strip()
    if not fecha_valida_para_busqueda(fecha):
        return mostrar_paso_horarios("Elegí una fecha desde mañana en adelante.")

    contexto, respuesta = contexto_paso_horarios()
    if respuesta is not None:
        return respuesta

    turnos, error, status = listar_turnos_disponibles(
        contexto["medico_id"],
        contexto["especialidad_id"],
        fecha,
    )
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        return mostrar_paso_horarios(error)
    disponibles = [turno for turno in (turnos or []) if turno.get("estado") == "disponible"]
    return mostrar_paso_horarios(turnos=disponibles)


@reservar_turno_bp.route("/reservar_turno/revisar", methods=["POST"])
def revisar_reserva():
    """
    sin errores se renderiza reservar_turno.html en el paso  con datos del turno y consulta
    """
    bloqueo = exigir_paciente()
    if bloqueo:
        return bloqueo
    
    fecha = request.form.get("fecha", "").strip()
    id_turno = request.form.get("id_turno", type=int)
    if not fecha_valida_para_busqueda(fecha):
        return mostrar_paso_horarios("Elegí una fecha desde mañana en adelante.")

    contexto, respuesta = contexto_paso_horarios()
    if respuesta is not None:
        return respuesta

    turnos, error, status = listar_turnos_disponibles(
        contexto["medico_id"], contexto["especialidad_id"], fecha
    )
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        return mostrar_paso_horarios(error)

    turno = next((item for item in (turnos or [])
                  if item.get("id_turno") == id_turno and item.get("estado") == "disponible"), None)
    if turno is None:
        return mostrar_paso_horarios("Ese horario ya no está disponible. Elegí otro.")
    return render_reserva(paso=3, turno=turno, **contexto)


@reservar_turno_bp.route("/reservar_turno/reservar", methods=["POST"])
def confirmar_reserva():
    """
    se termina el proceso con confirmacion del paciente
    """
    bloqueo = exigir_paciente()
    if bloqueo:
        return bloqueo
    id_turno = request.form.get("id_turno", type=int)
    if not id_turno or id_turno < 1:
        flash("Elegí un horario antes de confirmar.", "error")
        return redirect(url_for("reservar_turno.reservar_pantalla"))

    reserva, error, status = reservar_turno(id_turno)
    if error:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        flash(error, "error")
        return redirect(url_for("reservar_turno.reservar_pantalla"))

    especialidades, _, _ = listar_especialidades()
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