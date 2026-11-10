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
Pre: 'fecha' es una cadena ISO válida y 'presente' un objeto datetime.
Post: Devuelve la diferencia en minutos transcurridos.
"""
def minutos_desde(fecha: str, presente: datetime) -> int:
    try:
        return int((presente - datetime.fromisoformat(fecha)).total_seconds() // 60)
    except (ValueError, TypeError):
        return 0


"""
Pre: 'turno' es un diccionario con los datos del turno en sala de espera.
Post: Devuelve un diccionario adaptado para presentar en la interfaz.
"""
def formatear_turno_sala(turno: dict, ahora: datetime) -> dict:
    return {
        'paciente': turno.get('paciente', ''),
        'medico': turno.get('medico', ''),
        'consultorio': turno.get('consultorio', ''),
        'hora_llegada': formatear_hora(turno.get('fecha_hora_checkin')),
        'minutos_espera': minutos_desde(turno.get('fecha_hora_checkin', ''), ahora),
    }


"""
Pre: -
Post: Llama a la API del backend para obtener los turnos en sala de espera y los devuelve formateados para la vista.
"""
def obtener_sala_espera() -> list[dict]:
    presente = datetime.now()
    turnos, error, status = pedir('GET', '/recepcion/sala-espera')
    if error or not isinstance(turnos, list):
        return []
    return [formatear_turno_sala(turno, presente) for turno in turnos]


"""
Pre: 'token_qr' es un string no vacío correspondiente al código QR presentado.
Post: Llama a la API del backend para registrar la llegada y devuelve un diccionario con los datos del paciente y consultorio.
"""
def registrar_checkin(token_qr: str) -> dict:
    datos, error, status = pedir('POST', '/turnos/checkin', json={'token_qr': token_qr})

    if error:
        raise ValueError(error)

    return {
        'id_turno': datos.get('id_turno'),
        'paciente': datos.get('paciente', 'Paciente sin nombre'),
        'medico': datos.get('medico', 'Profesional asignado'),
        'consultorio': datos.get('consultorio', 'Consultorio asignado'),
        'hora_llegada': formatear_hora(datos.get('fecha_hora_checkin')),
        'hora_turno': formatear_hora(datos.get('fecha_hora')),
        'estado': datos.get('estado', 'confirmado'),
    }
