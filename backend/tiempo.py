from datetime import datetime, timedelta, timezone


def obtener_ahora_gmt3():
    """
    Pre: -
    Post: Devuelve la fecha y hora actual en hora de Argentina (GMT-3), sin zona horaria, para
          compararla con los campos DATETIME de MySQL (que se guardan en hora de Argentina). No
          depende de la zona horaria de la computadora o del servidor donde corre el backend.
    """
    zona_gmt3 = timezone(timedelta(hours=-3))
    return datetime.now(zona_gmt3).replace(tzinfo=None, microsecond=0)
