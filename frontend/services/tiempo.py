from datetime import datetime, timedelta, timezone


def obtener_ahora_gmt3():
    """
    Pre: -
    Post: Devuelve la fecha y hora actual en hora de Argentina (GMT-3), sin zona horaria, para
          compararla con las fechas que manda el backend (que también están en hora de Argentina).
          No depende de la zona horaria de la computadora donde corre el frontend.
    """
    zona_gmt3 = timezone(timedelta(hours=-3))
    return datetime.now(zona_gmt3).replace(tzinfo=None, microsecond=0)
