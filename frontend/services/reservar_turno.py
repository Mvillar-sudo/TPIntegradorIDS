from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from services.api_client import pedir
from datetime import datetime, timedelta, timezone


def listar_especialidades():
    """
    consulta especialidades disponibles en la APIconsulta especialidades disponibles en la API y devuelve una tupla (especialidades, error, status).
    """
    return pedir("GET", "/especialidades")


def listar_medicos(id_especialidad):
    """
    consulta médicos disponibles en la API y devuelve una tupla (medicos, error, status) 
    """
    medicos, error, status = pedir(
        "GET",
        "/medicos",
        params={"id_especialidad": id_especialidad},
    )
    if error:
        return None, error, status
    return medicos or [], None, status


def listar_turnos_disponibles(medico_id, id_especialidad, fecha):
    """
    consulta turnos disponibes segun los datos recibidos
    """
    return pedir(
        "GET",
        "/turnos/disponibles",
        params={
            "medico_id": medico_id,
            "id_especialidad": id_especialidad,
            "fecha": fecha,
        },
    )


def reservar_turno(id_turno):
    """
    crea un nuevo turno con estado reservado, codigo qr hash y datos del turno
    """
    return pedir(
        "POST",
        "/turnos/reservar",
        json={"id_turno": id_turno},
    )


def fecha_minima():
    """
    devuelve fecha minima segun 'dia actual + un dia' en formato ISO
    """
    zona_gmt3 = timezone(timedelta(hours=-3))
    return (datetime.now(zona_gmt3).date() + timedelta(days=1)).isoformat()


def fecha_valida_para_busqueda(fecha):
    """
    - si el formato de la fecha es invalido, devuelve false
    - Si es valido devuelve true si la fecha es mayor a fecha_minima()
    """
    try:
        fecha_parseada = datetime.strptime(fecha, "%Y-%m-%d")
    except (TypeError, ValueError):
        return False
    return fecha_parseada.strftime("%Y-%m-%d") == fecha and fecha >= fecha_minima()


def render_reserva(paso=1, especialidad_id="", medicos=None, medico_id="",
                    fecha="", turnos=None, turno=None, error=None,
                    medico_seleccionado=""):
    """
    Envia todos los datos necesarios para renderizar la pagina reservar_turno.html
    """
    especialidades, error_carga, _ = listar_especialidades()
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
        fecha_minima=fecha_minima(),
        turnos=turnos or [],
        turno=turno,
        medico_seleccionado=medico_seleccionado,
    )


def contexto_paso_horarios():
    """
    - Si los valores obtenidos son del tipo incorrecto/valor incorrecto, devuevlve vacio y mensaje de error
    - En caso de ocurrir un error del tipo error_medico:
        - Si el codigo es 401 el paciente ya no esta autenticado, se redirige a inicio de sesion
        - Si es otro error, se muestra mensaje de error_medicos
    - Si no existe el medico solicitado, devuelve mensaje de error_medicos
    - Todo sale bien, devuelve datos de consulta
    """
    especialidad_id = request.form.get("id_especialidad", "")
    medico_id = request.form.get("medico_id", "")
    fecha = request.form.get("fecha", "")

    try:
        especialidad_id = int(especialidad_id)
        medico_id = int(medico_id)
    except (TypeError, ValueError):
        return None, render_reserva(error="Seleccioná una especialidad y un médico válidos.")

    medicos, error_medicos, status = listar_medicos(especialidad_id)
    if error_medicos:
        if status == 401:
            session.clear()
            flash("Tu sesión expiró. Iniciá sesión nuevamente.", "error")
            return None, redirect(url_for("auth.iniciar_sesion"))
        return None, render_reserva(error=error_medicos)

    medico = None
    for item in medicos:
        if item.get("id_medico") == medico_id:
            medico = item

    if medico is None:
        return None, render_reserva(error="El médico elegido no pertenece a la especialidad.")

    etiqueta_medico = f"{medico.get('nombre_medico', '')} {medico.get('apellido_medico', '')}".strip()
    return {
        "especialidad_id": especialidad_id,
        "medicos": medicos,
        "medico_id": medico_id,
        "fecha": fecha,
        "medico_seleccionado": etiqueta_medico,
    }, None


def mostrar_paso_horarios(error=None, turnos=None):
    """
    devuelve turnos disponibles con los elementos del diccionario como argumentos de la función 
            (especialidad_id, medicos, medico_id, fecha y medico_seleccionado)
    """
    contexto, respuesta = contexto_paso_horarios()
    if respuesta is not None:
        return respuesta
    return render_reserva(paso=2, turnos=turnos, error=error, **contexto)
