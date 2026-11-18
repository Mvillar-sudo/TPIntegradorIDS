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
          Además trae 'dias_atencion' (checkboxes con los días de la semana en que se atiende).
    Post: Crea una agenda por cada día tildado dentro del rango de fechas, con la hora de inicio
          y de fin de ese día (así el backend no genera turnos fuera de ese horario). Devuelve
          (cantidad_creadas, errores), donde errores es una lista de textos "dd/mm: motivo" de
          los días que el backend rechazó. Lanza ValueError con un mensaje legible si falta algún
          dato o si el formulario no es válido.
    """
    campos = ('medico_id', 'consultorio_id', 'duracion_turno',
              'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin')

    if not all(formulario.get(campo) for campo in campos):
        raise ValueError('Completá el médico, el consultorio, las fechas, las horas y la duración del turno.')

    try:
        id_medico = int(formulario['medico_id'])
        id_consultorio = int(formulario['consultorio_id'])
        duracion = int(formulario['duracion_turno'])
    except ValueError:
        raise ValueError('El médico, el consultorio y la duración del turno tienen que ser números.') from None

    try:
        desde = date.fromisoformat(formulario['fecha_inicio'])
        hasta = date.fromisoformat(formulario['fecha_fin'])
    except ValueError:
        raise ValueError('Ingresá una fecha de inicio y de fin válidas.') from None

    hora_inicio = formulario['hora_inicio']
    hora_fin = formulario['hora_fin']
    dias = {DIAS_SEMANA[dia] for dia in formulario.getlist('dias_atencion') if dia in DIAS_SEMANA}

    if hasta < desde:
        raise ValueError('La fecha de fin no puede ser anterior a la de inicio.')
    if (hasta - desde).days > MAX_DIAS_RANGO:
        raise ValueError(f'El rango no puede superar {MAX_DIAS_RANGO} días.')
    if hora_fin <= hora_inicio:
        raise ValueError('La hora de fin debe ser posterior a la de inicio.')
    if not dias:
        raise ValueError('Tildá al menos un día de atención.')

    creadas = 0
    errores = []
    dia = desde
    while dia <= hasta:
        if dia.weekday() in dias:
            try:
                crear_agenda({
                    'id_medico': id_medico,
                    'id_consultorio': id_consultorio,
                    'agenda_fecha_hora_inicio': f'{dia.isoformat()} {hora_inicio}:00',
                    'agenda_fecha_hora_fin': f'{dia.isoformat()} {hora_fin}:00',
                    'duracion_turno_minutos': duracion,
                })
                creadas += 1
            except ValueError as error:
                errores.append(f'{dia.strftime("%d/%m")}: {error}')
        dia += timedelta(days=1)

    if creadas == 0 and not errores:
        raise ValueError('Ningún día del rango coincide con los días tildados.')

    return creadas, errores
