from datetime import datetime
from .datos_ejemplo import sala_espera_ejemplo, checkin_ejemplo

FORMATO_HORA = '%H:%M'


def formatear_hora(fecha: str) -> str:
    return datetime.fromisoformat(fecha).strftime(FORMATO_HORA)


def minutos_desde(fecha: str, presente: datetime) -> int:
    return int((presente - datetime.fromisoformat(fecha)).total_seconds() // 60)


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
    """Registra el check-in. Lanza ValueError si no se puede hacer."""
    resultado = checkin_ejemplo(token_qr) 

    return {
        'paciente': resultado['paciente'],
        'medico': resultado['medico'],
        'consultorio': resultado['consultorio'],
        'hora_llegada': formatear_hora(resultado['fecha_hora_checkin']),
    }