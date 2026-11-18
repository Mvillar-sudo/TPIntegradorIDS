from datetime import date, timedelta

from services.api_client import pedir

DIAS_SEMANA = {'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6}
MAX_DIAS_RANGO = 90


def obtener_medicos():
    """Devuelve la lista de médicos del backend. Lanza ValueError con el mensaje si falla."""
    datos, error, _ = pedir('GET', '/medicos')

    if error:
        raise ValueError(error)

    return datos


def obtener_consultorios():
    """Devuelve la lista de consultorios del backend. Lanza ValueError con el mensaje si falla."""
    datos, error, _ = pedir('GET', '/consultorios')

    if error:
        raise ValueError(error)

    return datos


def crear_agenda(datos_formateados):
    """Crea la agenda en el backend (POST /agendas). Lanza ValueError con el mensaje si falla."""
    datos, error, _ = pedir('POST', '/agendas', json=datos_formateados, timeout=30)

    if error:
        raise ValueError(error)

    return datos


def crear_agenda_desde_formulario(formulario):
    """
    Pre: 'formulario' es el formulario de la pantalla de agendas (request.form), con medico_id,
         consultorio_id, duracion_turno, fecha_inicio, hora_inicio, fecha_fin y hora_fin.
    Post: Arma los datos como los pide el backend y crea la agenda. Devuelve la respuesta del
          backend. Lanza ValueError con un mensaje legible si falta algún dato o si el backend
          rechaza la agenda.
    """
    campos = ('medico_id', 'consultorio_id', 'duracion_turno',
              'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin')

    if not all(formulario.get(campo) for campo in campos):
        raise ValueError('Completá el médico, el consultorio, las fechas, las horas y la duración del turno.')

    try:
        datos_backend = {
            'id_medico': int(formulario['medico_id']),
            'id_consultorio': int(formulario['consultorio_id']),
            'agenda_fecha_hora_inicio': f"{formulario['fecha_inicio']} {formulario['hora_inicio']}:00",
            'agenda_fecha_hora_fin': f"{formulario['fecha_fin']} {formulario['hora_fin']}:00",
            'duracion_turno_minutos': int(formulario['duracion_turno']),
        }
    except ValueError:
        raise ValueError('El médico, el consultorio y la duración del turno tienen que ser números.') from None

    return crear_agenda(datos_backend)
