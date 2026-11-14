from datetime import datetime

from flask import session

from .api_client import pedir

FORMATO_HORA = '%H:%M'

def formatear_hora(fecha: str | None) -> str:
    if not fecha:
        return '-'
    try:
        return datetime.fromisoformat(fecha).strftime(FORMATO_HORA)
    except (ValueError, TypeError):
        return '-'

def formatear_turno_medico(turno: dict) -> dict:
    return {
        'id_turno': turno.get('id_turno') or turno.get('id'),
        'paciente': turno.get('paciente'),
        'dni': turno.get('paciente_dni'),
        'hora': formatear_hora(turno.get('fecha_hora')),
        'hora_llegada': formatear_hora(turno.get('fecha_hora_checkin')),
        'estado': turno.get('estado'),
        'puede_atender': turno.get('estado') == 'confirmado',
    }

def obtener_perfil_medico() -> dict:
    usuario = session.get('usuario', {})
    return {
        'nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() or 'Médico'
    }

def obtener_turnos_hoy():
    datos, error, status = pedir('GET', '/medicos/turnos/hoy')
    if error:
        return [], error, status

    turnos_formateados = [formatear_turno_medico(turno) for turno in datos['turnos_hoy']]
    return turnos_formateados, None, status

def registrar_turno_atendido(id_turno: int):
    return pedir('PATCH', f'/medicos/turnos/{id_turno}/atendido')
