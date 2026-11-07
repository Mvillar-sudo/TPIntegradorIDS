from datetime import datetime
from services.api_client import pedir
from .datos_ejemplo import sala_espera_ejemplo

FORMATO_HORA = '%H:%M'


def formatear_hora(fecha: str | None) -> str:
    if not fecha:
        return '-'
    try:
        return datetime.fromisoformat(fecha).strftime(FORMATO_HORA)
    except (ValueError, TypeError):
        return str(fecha)


def minutos_desde(fecha: str, presente: datetime) -> int:
    try:
        return int((presente - datetime.fromisoformat(fecha)).total_seconds() // 60)
    except (ValueError, TypeError):
        return 0


def formatear_turno_sala(turno: dict, ahora: datetime) -> dict:
    return {
        'paciente': turno['paciente'],
        'medico': turno['medico'],
        'consultorio': turno['consultorio'],
        'hora_llegada': formatear_hora(turno['fecha_hora_checkin']),
        'minutos_espera': minutos_desde(turno['fecha_hora_checkin'], ahora),
    }


def obtener_sala_espera() -> list[dict]:
    """Sala de espera lista para mostrar (el backend ya la manda ordenada por llegada)."""
    presente = datetime.now()
    turnos = sala_espera_ejemplo()

    return [formatear_turno_sala(turno, presente) for turno in turnos]


def registrar_checkin(token_qr: str) -> dict:
    """Registra el check-in en el backend real. Lanza ValueError si no se puede hacer."""
    datos, error, status = pedir('POST', '/turnos/checkin', json={'token_qr': token_qr})

    if error:
        raise ValueError(error)

    return {
        'paciente': datos.get('paciente', ''),
        'medico': datos.get('medico', 'Profesional asignado'),
        'consultorio': datos.get('consultorio', 'Consultorio asignado'),
        'hora_llegada': formatear_hora(datos.get('fecha_hora_checkin')),
    }
