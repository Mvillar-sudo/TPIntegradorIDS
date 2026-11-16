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
        'dni': turno.get('paciente_dni') or turno.get('dni') or '-',
        'hora': formatear_hora(turno.get('fecha_hora')),
        'hora_llegada': formatear_hora(turno.get('fecha_hora_checkin')),
        'estado': turno.get('estado'),
        'puede_atender': turno.get('estado') == 'confirmado',
    }


def obtener_perfil_medico(id_medico: int | None = None) -> dict:
    usuario_sesion = session.get('usuario') or {}
    nombre_sesion = f"{usuario_sesion.get('nombre', '')} {usuario_sesion.get('apellido', '')}".strip()

    perfil = {
        'nombre': nombre_sesion or 'Médico de Guardia',
        'especialidad': 'No especificada',
        'consultorio': 'Sin asignar',
    }

    if not id_medico:
        return perfil

    datos, error, _ = pedir('GET', f'/medicos/{id_medico}')
    if error or not isinstance(datos, dict):
        return perfil

    nombre_api = f"{datos.get('nombre_medico', '')} {datos.get('apellido_medico', '')}".strip()
    if nombre_api:
        perfil['nombre'] = nombre_api
    if datos.get('especialidad'):
        perfil['especialidad'] = datos['especialidad']
    if datos.get('consultorio'):
        perfil['consultorio'] = datos['consultorio']

    return perfil


def obtener_turnos_y_medico_hoy():
    datos, error, status = pedir('GET', '/medicos/turnos/hoy')
    if error or not datos:
        return [], None, error or "No se pudieron obtener los turnos", status

    if isinstance(datos, dict):
        id_medico = datos.get('id_medico')
        lista_turnos = datos.get('turnos_hoy', [])
    else:
        id_medico = None
        lista_turnos = datos

    turnos_formateados = [formatear_turno_medico(turno) for turno in lista_turnos]
    return turnos_formateados, id_medico, None, status



def registrar_turno_atendido(id_turno: int):
    return pedir('PATCH', f'/medicos/turnos/{id_turno}/atendido')
