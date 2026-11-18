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


def crear_agendas_por_dia(form):
    """Crea una agenda por cada día tildado dentro del rango, con su hora de inicio y de fin.

    Devuelve (cantidad_creadas, errores), donde errores es una lista de textos "dd/mm: motivo".
    Lanza ValueError si el formulario es inválido.
    """
    try:
        desde = date.fromisoformat(form.get('fecha_inicio', ''))
        hasta = date.fromisoformat(form.get('fecha_fin', ''))
    except ValueError:
        raise ValueError('Ingresá una fecha de inicio y de fin válidas.') from None

    h_inicio = form.get('hora_inicio', '')
    h_fin = form.get('hora_fin', '')
    dias = {DIAS_SEMANA[d] for d in form.getlist('dias_atencion') if d in DIAS_SEMANA}

    if hasta < desde:
        raise ValueError('La fecha de fin no puede ser anterior a la de inicio.')
    if (hasta - desde).days > MAX_DIAS_RANGO:
        raise ValueError(f'El rango no puede superar {MAX_DIAS_RANGO} días.')
    if not h_inicio or not h_fin or h_fin <= h_inicio:
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
                    'id_medico': int(form.get('medico_id')),
                    'id_consultorio': int(form.get('consultorio_id')),
                    'agenda_fecha_hora_inicio': f'{dia.isoformat()} {h_inicio}:00',
                    'agenda_fecha_hora_fin': f'{dia.isoformat()} {h_fin}:00',
                    'duracion_turno_minutos': int(form.get('duracion_turno', 60)),
                })
                creadas += 1
            except ValueError as error:
                errores.append(f'{dia.strftime("%d/%m")}: {error}')
        dia += timedelta(days=1)

    if creadas == 0 and not errores:
        raise ValueError('Ningún día del rango coincide con los días tildados.')
    return creadas, errores
