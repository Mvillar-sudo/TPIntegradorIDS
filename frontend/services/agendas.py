from services.api_client import pedir


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
