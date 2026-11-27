from datetime import datetime, timedelta

_turnos_mock = None


def _obtener_lista_turnos() -> list[dict]:
    global _turnos_mock
    if _turnos_mock is None:
        ahora = datetime.now()
        _turnos_mock = [
            {
                'id_turno': 45,
                'paciente': 'García, Juan',
                'dni': '12345678',
                'fecha_hora': (ahora - timedelta(minutes=15)).isoformat(timespec='seconds'),
                'fecha_hora_checkin': (ahora - timedelta(minutes=15)).isoformat(timespec='seconds'),
                'estado': 'confirmado',
                'consultorio': '102',
            },
            {
                'id_turno': 46,
                'paciente': 'López, María',
                'dni': '87654321',
                'fecha_hora': ahora.isoformat(timespec='seconds'),
                'fecha_hora_checkin': (ahora - timedelta(minutes=5)).isoformat(timespec='seconds'),
                'estado': 'confirmado',
                'consultorio': '102',
            },
            {
                'id_turno': 47,
                'paciente': 'Martínez, Laura',
                'dni': '55667788',
                'fecha_hora': (ahora + timedelta(minutes=20)).isoformat(timespec='seconds'),
                'fecha_hora_checkin': None,
                'estado': 'reservado',
                'consultorio': '102',
            },
            {
                'id_turno': 44,
                'paciente': 'Rodríguez, Pablo',
                'dni': '44332211',
                'fecha_hora': (ahora - timedelta(minutes=40)).isoformat(timespec='seconds'),
                'fecha_hora_checkin': (ahora - timedelta(minutes=40)).isoformat(timespec='seconds'),
                'estado': 'atendido',
                'consultorio': '102',
            },
            {
                'id_turno': 43,
                'paciente': 'Fernández, Carlos',
                'dni': '33445566',
                'fecha_hora': (ahora - timedelta(hours=1)).isoformat(timespec='seconds'),
                'fecha_hora_checkin': None,
                'estado': 'ausente',
                'consultorio': '102',
            },
        ]
    return _turnos_mock


"""
Pre: -
Post: Devuelve un diccionario simulando el perfil del médico autenticado.
"""
def perfil_medico_ejemplo() -> dict:
    return {
        'nombre': 'Dr. Carlos Pérez',
        'consultorio': '102 (Planta Baja)',
        'especialidad': 'Cardiología',
    }


"""
Pre: -
Post: Devuelve una lista de diccionarios simulando la respuesta JSON de GET /api/v1/medicos/turnos/hoy.
"""
def turnos_hoy_medico_ejemplo() -> list[dict]:
    return _obtener_lista_turnos()


"""
Pre: 'id_turno' es un entero positivo.
Post: Valida el turno, actualiza su estado a 'atendido' en memoria y devuelve la respuesta simulada.
"""
def atender_turno_ejemplo(id_turno: int) -> dict:
    turnos = _obtener_lista_turnos()
    for t in turnos:
        if t['id_turno'] == id_turno:
            if t['estado'] != 'confirmado':
                raise ValueError(f'No se puede atender el turno #{id_turno} porque no está confirmado')
            t['estado'] = 'atendido'
            return {
                'id_turno': id_turno,
                'estado': 'atendido',
                'mensaje': 'Turno marcado como atendido exitosamente',
            }
    raise ValueError(f'Turno #{id_turno} no encontrado')
