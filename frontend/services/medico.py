from datetime import datetime
from services.api_client import pedir

FORMATO_HORA = '%H:%M'

"""
Pre: 'fecha' es una cadena ISO válida de fecha/hora, o None.
Post: Devuelve la hora formateada en 'HH:MM' o '-' si 'fecha' es nula o vacía.
"""
def formatear_hora(fecha: str | None) -> str:

    if not fecha:
        return '-'
    try:
        return datetime.fromisoformat(fecha).strftime(FORMATO_HORA)
    except (ValueError, TypeError):
        return '-'

"""
Pre: 'turno' es un diccionario con la clave 'hora'.
Post: Devuelve la hora formateada del turno como clave para ordenar cronológicamente.
"""
def criterio_orden_turno(turno: dict) -> str:
    return turno.get('hora', '')

"""
Pre: 'turno' es un diccionario con las claves 'hora_llegada' y 'hora'.
Post: Devuelve la hora de llegada o la hora programada para ordenar la sala de espera.
"""
def criterio_orden_llegada(turno: dict) -> str:
    hora_llegada = turno.get('hora_llegada')
    if hora_llegada and hora_llegada != '-':
        return hora_llegada
    return turno.get('hora', '')

"""
Pre: 'turno' es un diccionario con los campos del turno (id_turno, paciente, dni, fecha_hora, fecha_hora_checkin, estado).
Post: Devuelve un diccionario adaptado para presentar en la interfaz.
"""
def formatear_turno_medico(turno: dict) -> dict:
    return {
        'id_turno': turno['id_turno'],
        'paciente': turno.get('paciente') or 'Paciente sin nombre',
        'dni': turno.get('paciente_dni') or turno.get('dni') or '-',
        'hora': formatear_hora(turno.get('fecha_hora')),
        'hora_llegada': formatear_hora(turno.get('fecha_hora_checkin')),
        'estado': turno.get('estado', 'desconocido'),
        'puede_atender': turno.get('estado') == 'confirmado',
    }

"""
Pre: El usuario debe encontrarse autenticado con rol médico.
Post: Consulta la API del backend para obtener el perfil y la agenda de turnos de hoy.
Devuelve ValueError en caso de error o si el usuario no es un médico registrado.
"""
def obtener_agenda_medico() -> tuple[dict, list[dict]]:
    datos, error, status = pedir('GET', '/medicos/turnos/hoy')

    if error:
        raise ValueError(error)

    medico_api = datos.get('medico', {}) if isinstance(datos, dict) else {}
    turnos_raw = datos.get('turnos_hoy', []) if isinstance(datos, dict) else []
    turnos = [formatear_turno_medico(t) for t in turnos_raw]
    turnos.sort(key=criterio_orden_turno)

    consultorio = '-'
    if turnos_raw and turnos_raw[0].get('consultorio'):
        consultorio = turnos_raw[0]['consultorio']

    perfil = {
        'nombre': medico_api.get('nombre') or 'Profesional Médico',
        'consultorio': consultorio,
        'especialidad': medico_api.get('especialidad') or 'General',
    }

    turnos_espera = [t for t in turnos if t.get('estado') == 'confirmado']
    turnos_espera.sort(key=criterio_orden_llegada)

    return perfil, turnos, turnos_espera

"""
Pre: 'id_turno' es un entero positivo correspondiente a un turno en estado 'confirmado'.
Post: Marca el turno como atendido en el backend y devuelve la respuesta. 
Devuelve ValueError si el backend rechaza la operación.
"""
def registrar_turno_atendido(id_turno: int) -> dict:
    datos, error, status = pedir('PATCH', f'/medicos/turnos/{id_turno}/atendido')

    if error:
        raise ValueError(error)

    return datos
