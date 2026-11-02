from datetime import datetime

from ..constants import MAX_DIAS_AGENDA, MAX_DURACION_MINUTOS
from ..utils import validar_entero_positivo, validar_objeto_json


def _datetime(value, field):
    if not isinstance(value, str):
        raise ValueError(f"El campo '{field}' debe ser una fecha y hora ISO 8601") #ejemplo:2026-11-10T09:00:00
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"El campo '{field}' debe ser una fecha y hora ISO 8601") from None
    if parsed.tzinfo is not None:
        raise ValueError(f"El campo '{field}' no debe incluir zona horaria")
    return parsed


def validar_agenda(body):
    body = validar_objeto_json(body)
    allowed = {
        'id_medico',
        'id_consultorio',
        'agenda_fecha_hora_inicio',
        'agenda_fecha_hora_fin',
        'duracion_turno_minutos',
    }
    unknown = set(body) - allowed
    if unknown:
        raise ValueError(f"Campos no permitidos: {', '.join(sorted(unknown))}")

    result = {
        'id_medico': validar_entero_positivo(body.get('id_medico'), 'id_medico'),
        'id_consultorio': validar_entero_positivo(body.get('id_consultorio'), 'id_consultorio'),
    }
    result['agenda_fecha_hora_inicio'] = _datetime(
        body.get('agenda_fecha_hora_inicio'), 'agenda_fecha_hora_inicio'
    )
    result['agenda_fecha_hora_fin'] = _datetime(
        body.get('agenda_fecha_hora_fin'), 'agenda_fecha_hora_fin'
    )
    if result['agenda_fecha_hora_inicio'] <= datetime.now():
        raise ValueError('agenda_fecha_hora_inicio debe ser futura')
    if result['agenda_fecha_hora_fin'] <= result['agenda_fecha_hora_inicio']:
        raise ValueError('agenda_fecha_hora_fin debe ser posterior al inicio')
    if (result['agenda_fecha_hora_fin'] - result['agenda_fecha_hora_inicio']).days > MAX_DIAS_AGENDA:
        raise ValueError('El período de la agenda no puede superar un año')

    result['duracion_turno_minutos'] = validar_entero_positivo(
        body.get('duracion_turno_minutos'), 'duracion_turno_minutos'
    )
    if result['duracion_turno_minutos'] > MAX_DURACION_MINUTOS:
        raise ValueError('La duración del turno no puede superar 60 minutos')
    available_minutes = (
        result['agenda_fecha_hora_fin'] - result['agenda_fecha_hora_inicio']
    ).total_seconds() / 60
    if result['duracion_turno_minutos'] > available_minutes:
        raise ValueError('La duración del turno supera el período de la agenda')
    return result