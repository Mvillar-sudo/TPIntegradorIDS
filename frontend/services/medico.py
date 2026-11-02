from datetime import datetime
from .datos_medico_ejemplo import (
    turnos_hoy_medico_ejemplo,
    atender_turno_ejemplo,
    perfil_medico_ejemplo,
)

FORMATO_HORA = '%H:%M'

"""
Pre: -
Post: Devuelve los datos del perfil del profesional médico para la cabecera de la vista.
"""
def obtener_perfil_medico() -> dict:
    return perfil_medico_ejemplo()

"""
Pre: 'fecha' es una cadena ISO válida de fecha/hora, o None.
Post: Devuelve la hora formateada en 'HH:MM' o '-' si 'fecha' es nula o vacía.
"""
def formatear_hora(fecha: str | None) -> str:
    if not fecha:
        return '-'
    return datetime.fromisoformat(fecha).strftime(FORMATO_HORA)

"""
Pre: 'turno' es un diccionario con los campos del turno (id_turno, paciente, dni, fecha_hora, fecha_hora_checkin, estado).
Post: Devuelve un diccionario adaptado para presentar en la interfaz.
"""
def formatear_turno_medico(turno: dict) -> dict:
    return {
        'id_turno': turno['id_turno'],
        'paciente': turno['paciente'],
        'dni': turno['dni'],
        'hora': formatear_hora(turno['fecha_hora']),
        'hora_llegada': formatear_hora(turno['fecha_hora_checkin']),
        'estado': turno['estado'],
        'puede_atender': turno['estado'] == 'confirmado',
    }

"""
Pre: -
Post: Devuelve la lista de turnos del día asignados al médico, formateados y listos para mostrar.
"""
def obtener_turnos_hoy() -> list[dict]:
    turnos = turnos_hoy_medico_ejemplo()
    return [formatear_turno_medico(turno) for turno in turnos]

"""
Pre: 'id_turno' es un entero positivo correspondiente a un turno en estado 'confirmado'.
Post: Marca el turno como atendido y devuelve el diccionario de resultado.
"""
def registrar_turno_atendido(id_turno: int) -> dict:
    return atender_turno_ejemplo(id_turno)
