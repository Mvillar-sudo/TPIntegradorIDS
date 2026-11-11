try:
    from repositories.recepcion import obtener_turnos_sala_espera as repo_obtener_turnos_sala_espera
except ImportError:
    from backend.repositories.recepcion import obtener_turnos_sala_espera as repo_obtener_turnos_sala_espera


"""
Pre: 'dt' es un objeto datetime o None.
Post: Devuelve una cadena con formato ISO 'YYYY-MM-DDTHH:MM:SS' o None si dt es nulo.
"""
def formatear_fecha_iso(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")


"""
Pre: -
Post: Obtiene los turnos confirmados en sala de espera y devuelve una lista de diccionarios.
"""
def obtener_sala_espera():
    turnos = repo_obtener_turnos_sala_espera()
    resultado = []

    for t in turnos:
        paciente_nom = t.get("paciente_nombre") or ""
        paciente_ape = t.get("paciente_apellido") or ""
        if paciente_ape and paciente_nom:
            paciente = f"{paciente_ape}, {paciente_nom}"
        else:
            paciente = f"{paciente_nom} {paciente_ape}".strip() or "Paciente sin nombre"

        medico_nom = f"{t.get('medico_nombre', '')} {t.get('medico_apellido', '')}".strip()
        medico = f"Dr. {medico_nom}" if medico_nom else "Profesional asignado"

        consultorio = str(t.get("numero_consultorio") or "Consultorio asignado")

        resultado.append({
            "id_turno": t["id_turno"],
            "paciente": paciente,
            "medico": medico,
            "consultorio": consultorio,
            "fecha_hora_checkin": formatear_fecha_iso(t.get("fecha_hora_checkin")),
        })

    return resultado
