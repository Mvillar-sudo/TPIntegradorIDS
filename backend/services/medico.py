try:
    from repositories.medico import (
        obtener_medico_por_usuario_id,
        obtener_turnos_hoy_por_medico,
        buscar_turno_por_id,
        actualizar_turno_a_atendido,
    )
except ImportError:
    from backend.repositories.medico import (
        obtener_medico_por_usuario_id,
        obtener_turnos_hoy_por_medico,
        buscar_turno_por_id,
        actualizar_turno_a_atendido,
    )


"""
Pre: 'dt' es un objeto datetime o None.
Post: Formatea 'dt' como 'YYYY-MM-DDTHH:MM:SS'. Retorna None si 'dt' es None.
"""
def formatear_fecha_iso(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")


"""
Pre: 'turno' es un diccionario con los datos de un turno obtenido de la consulta SQL.
Post: Retorna un diccionario con los datos del turno formateados para la respuesta JSON.
"""
def _formatear_turno(turno):
    nombre = turno.get("paciente_nombre") or ""
    apellido = turno.get("paciente_apellido") or ""
    paciente = f"{nombre} {apellido}".strip()

    return {
        "id_turno": turno["id_turno"],
        "fecha_hora_inicio": formatear_fecha_iso(turno["fecha_hora_inicio"]),
        "fecha_hora_fin": formatear_fecha_iso(turno["fecha_hora_fin"]),
        "estado": turno["estado"],
        "fecha_hora_checkin": formatear_fecha_iso(turno.get("fecha_hora_checkin")),
        "paciente": paciente,
        "paciente_dni": turno["paciente_dni"],
    }


"""
Pre: 'id_usuario' es un entero positivo correspondiente a un usuario con rol 'medico'.
Post: Retorna una tupla (respuesta_json, status_code) con los turnos del día del médico.
"""
def listar_turnos_hoy_servicio(id_usuario):
    medico = obtener_medico_por_usuario_id(id_usuario)
    if not medico:
        return {"error": "Usuario no registrado como médico"}, 403

    turnos = obtener_turnos_hoy_por_medico(medico["id_medico"])
    turnos_formateados = [_formatear_turno(t) for t in turnos]

    return {"id_medico": medico["id_medico"], "turnos_hoy": turnos_formateados}, 200


"""
Pre: 'id_usuario' es un entero positivo, 'id_turno' es un entero positivo.
Post: Marca el turno como 'atendido' si pertenece al médico y está en estado 'confirmado'.
      Retorna una tupla (respuesta_json, status_code).
"""
def marcar_atendido_servicio(id_usuario, id_turno):
    medico = obtener_medico_por_usuario_id(id_usuario)
    if not medico:
        return {"error": "Usuario no registrado como médico"}, 403

    turno = buscar_turno_por_id(id_turno)
    if turno is None:
        return {"error": "Turno no encontrado"}, 404

    if turno["id_medico"] != medico["id_medico"]:
        return {"error": "El turno no corresponde al profesional médico autenticado"}, 403

    estado_actual = turno["estado"]

    if estado_actual == "atendido":
        return {"error": "El turno ya fue marcado como atendido previamente"}, 400

    if estado_actual != "confirmado":
        return {
            "error": f"No se puede marcar como atendido un turno en estado '{estado_actual}'. Debe estar confirmado"
        }, 400

    exito = actualizar_turno_a_atendido(id_turno, medico["id_medico"])
    if not exito:
        return {"error": "No se pudo marcar como atendido el turno"}, 400

    return {
        "id_turno": id_turno,
        "estado": "atendido",
        "mensaje": "Turno marcado como atendido exitosamente"
    }, 200
