from datetime import datetime
from .datos_ejemplo import sala_espera_ejemplo, checkin_ejemplo

FORMATO_HORA = '%H:%M'


def formatearHora(fecha: str) -> str:
    return datetime.fromisoformat(fecha).strftime(FORMATO_HORA)


def minutosDesde(fecha: str, presente: datetime) -> int:
    return int((presente - datetime.fromisoformat(fecha)).total_seconds() // 60)


def formatearTurnoSala(turno: dict, ahora: datetime) -> dict:
    return {
        'paciente': turno['paciente'],
        'medico': turno['medico'],
        'consultorio': turno['consultorio'],
        'hora_llegada': formatearHora(turno['fecha_hora_checkin']),
        'minutos_espera': minutosDesde(turno['fecha_hora_checkin'], ahora),
    }


def obtenerSalaEspera() -> list[dict]:
    """Sala de espera lista para mostrar (el backend ya la manda ordenada por llegada)."""
    presente = datetime.now()
    turnos = sala_espera_ejemplo()

    return [formatearTurnoSala(turno, presente) for turno in turnos]


def registrarCheckin(token_qr: str) -> dict:
    """Registra el check-in. Lanza ValueError si no se puede hacer."""
    resultado = checkinEjemplo(token_qr) 

    return {
        'paciente': resultado['paciente'],
        'medico': resultado['medico'],
        'consultorio': resultado['consultorio'],
        'hora_llegada': formatearHora(resultado['fechaHoraCheckin']),
    }