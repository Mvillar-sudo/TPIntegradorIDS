from datetime import datetime

from services.api_client import pedir

FORMATO_FECHA = '%d/%m/%Y %H:%M'
ESTADOS_PROXIMOS = ('reservado', 'confirmado')


def formatear_fecha(fecha_iso):
    """
    Pre: 'fecha_iso' es un string de fecha y hora en formato ISO (por ejemplo '2026-11-10T09:00:00').
    Post: Devuelve la fecha y hora como texto legible ('10/11/2026 09:00').
    """
    return datetime.fromisoformat(fecha_iso).strftime(FORMATO_FECHA)


def listar_mis_turnos():
    """
    Pre: hay un paciente con sesión iniciada.
    Post: Devuelve una tupla (datos, error, status). Si salió bien, 'datos' es un diccionario con
          'proximos' (turnos reservados o confirmados, el más cercano primero) y 'anteriores'
          (atendidos, cancelados y ausentes, el más reciente primero). Cada turno trae
          'fecha_hora_texto' ya formateada.
    """
    turnos, error, status = pedir('GET', '/turnos/mis-turnos')

    if error is not None:
        return None, error, status

    for turno in turnos:
        turno['fecha_hora_texto'] = formatear_fecha(turno['fecha_hora'])

    proximos = [turno for turno in turnos if turno['estado'] in ESTADOS_PROXIMOS]
    anteriores = [turno for turno in turnos if turno['estado'] not in ESTADOS_PROXIMOS]
    proximos.reverse()

    return {'proximos': proximos, 'anteriores': anteriores}, None, status


def obtener_mi_turno(id_turno):
    """
    Pre: 'id_turno' es un entero positivo y hay un paciente con sesión iniciada.
    Post: Devuelve una tupla (turno, error, status). 'turno' es el diccionario del turno con
          'fecha_hora_texto' ya formateada, o None si falló. Si el turno no existe o no es del
          paciente, devuelve (None, mensaje, 404).
    """
    datos, error, status = listar_mis_turnos()

    if error is not None:
        return None, error, status

    for turno in datos['proximos'] + datos['anteriores']:
        if turno['id_turno'] == id_turno:
            return turno, None, status

    return None, 'No encontramos ese turno entre tus turnos', 404


def cancelar_turno(id_turno):
    """
    Pre: 'id_turno' es un entero positivo y hay una sesión iniciada.
    Post: Pide al backend cancelar el turno y devuelve la tupla (datos, error, status) de
          api_client.pedir().
    """
    return pedir('POST', f'/turnos/{id_turno}/cancelar')


def obtener_qr(id_turno):
    """
    Pre: 'id_turno' es un entero positivo y hay una sesión iniciada.
    Post: Devuelve una tupla (imagen, error, status). 'imagen' son los bytes del PNG con el QR del
          turno, o None si el backend no lo da (turno ajeno, cancelado, inexistente...).
    """
    return pedir('GET', f'/turnos/{id_turno}/qr', binario=True)
