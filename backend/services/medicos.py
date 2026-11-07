from repositories import medicos


def listar(especialidad_id=None):
    return medicos.listar_medicos(especialidad_id)


def obtener(medico_id):
    item = medicos.obtener_medico(medico_id)
    if item is None:
        raise LookupError('No se encontró el médico solicitado')
    return item


def crear(values):
    if not medicos.especialidad_existe(values['id_especialidad']):
        raise ValueError('La especialidad indicada no existe')
    if medicos.matricula_existe(values['matricula']):
        raise ValueError('La matrícula ingresada ya existe')
    return medicos.crear_medico(values)


def actualizar(medico_id, values):
    obtener(medico_id)
    if 'id_especialidad' in values and not medicos.especialidad_existe(values['id_especialidad']):
        raise ValueError('La especialidad indicada no existe')
    if 'matricula' in values and medicos.matricula_existe(values['matricula'], medico_id):
        raise ValueError('La matrícula ingresada ya existe')
    medicos.actualizar_medico(medico_id, values)
    return obtener(medico_id)


def eliminar(medico_id):
    obtener(medico_id)
    if medicos.tiene_dependencias(medico_id):
        raise ValueError('No se puede eliminar un médico con agendas o turnos asociados')
    medicos.eliminar_medico(medico_id)


def formatear_fecha_iso(dt):
    """
    Pre: 'dt' es un objeto datetime o None.
    Post: Formatea 'dt' como 'YYYY-MM-DDTHH:MM:SS'.
    """
    if dt is None:
        return None
    return dt.replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")


def _formatear_turno(turno):
    """
    Pre: 'turno' es un diccionario con los datos de un turno obtenido de la consulta SQL.
    Post: Devuelve un diccionario con los datos del turno formateados para la respuesta JSON.
    """
    nombre = turno.get("paciente_nombre") or ""
    apellido = turno.get("paciente_apellido") or ""
    paciente = f"{nombre} {apellido}".strip()

    return {
        "id_turno": turno["id_turno"],
        "fecha_hora": formatear_fecha_iso(turno.get("fecha_hora")),
        "estado": turno["estado"],
        "token_qr": turno.get("token_qr"),
        "fecha_hora_checkin": formatear_fecha_iso(turno.get("fecha_hora_checkin")),
        "paciente": paciente,
        "paciente_dni": turno.get("paciente_dni"),
    }


def listar_turnos_hoy_servicio(id_usuario):
    """
    Pre: 'id_usuario' es un entero positivo correspondiente a un usuario con rol 'medico'.
    Post: Devuelve una tupla (respuesta_json, status_code) con los turnos del día del médico y el código de estado.
    """
    medico = medicos.obtener_medico_por_usuario_id(id_usuario)

    if not medico:
        return {"error": "Usuario no registrado como médico"}, 403

    turnos = medicos.obtener_turnos_hoy_por_medico(medico["id_medico"])
    turnos_formateados = [_formatear_turno(t) for t in turnos]

    return {"id_medico": medico["id_medico"], "turnos_hoy": turnos_formateados}, 200


def marcar_atendido_servicio(id_usuario, id_turno):
    """
    Pre: 'id_usuario' es un entero positivo, 'id_turno' es un entero positivo.
    Post: Marca el turno como 'atendido' si pertenece al médico y está en estado 'confirmado'.
    Devuelve una tupla (respuesta_json, status_code).
    """
    medico = medicos.obtener_medico_por_usuario_id(id_usuario)

    if not medico:
        return {"error": "Usuario no registrado como médico"}, 403

    turno = medicos.buscar_turno_por_id(id_turno)

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

    exito = medicos.actualizar_turno_a_atendido(id_turno, medico["id_medico"])

    if not exito:
        return {"error": "No se pudo marcar como atendido el turno"}, 400

    return {
        "id_turno": id_turno,
        "estado": "atendido",
        "mensaje": "Turno marcado como atendido exitosamente",
    }, 200
