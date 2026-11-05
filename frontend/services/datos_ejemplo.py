from datetime import datetime, timedelta

TOKEN_QR_EJEMPLO = 'qr_valido_123'


def sala_espera_ejemplo() -> list[dict]:
    """Imita la respuesta de GET /api/v1/recepcion/sala-espera (endpoint 11 del Hito 1)."""
    presente = datetime.now()

    return [
        {'id_turno': 45, 'paciente': 'López, María', 'medico': 'Dr. Gómez', 'consultorio': '204',
         'fecha_hora_checkin': (presente - timedelta(minutes=25)).isoformat(timespec='seconds')},
        {'id_turno': 46, 'paciente': 'García, Juan', 'medico': 'Dr. Pérez', 'consultorio': '102',
         'fecha_hora_checkin': (presente - timedelta(minutes=20)).isoformat(timespec='seconds')},
        {'id_turno': 47, 'paciente': 'Rodríguez, Pablo', 'medico': 'Dra. Sosa', 'consultorio': '105',
         'fecha_hora_checkin': (presente - timedelta(minutes=8)).isoformat(timespec='seconds')},
    ]


def checkin_ejemplo(token_qr: str) -> dict:
    """Imita la respuesta de POST /api/v1/turnos/checkin."""
    if token_qr != TOKEN_QR_EJEMPLO:
        raise ValueError('Código QR inválido o turno no encontrado')

    return {'paciente': 'García, Juan', 'medico': 'Dr. Pérez', 'consultorio': '102',
            'fecha_hora_checkin': datetime.now().isoformat(timespec='seconds')}