from datetime import datetime


def validar_id_opcional(valor, nombre_parametro):
    if valor is None:
        return None, None

    try:
        identificador = int(valor)
    except ValueError:
        return None, f"El parámetro {nombre_parametro} debe ser un número entero válido."

    if identificador <= 0:
        return None, f"El parámetro {nombre_parametro} debe ser un entero positivo."

    return identificador, None


def validar_fecha_opcional(fecha):
    if fecha is None:
        return None, None

    try:
        fecha_validada = datetime.strptime(fecha, "%Y-%m-%d")

        # strptime puede aceptar algunas representaciones no canónicas.
        # Comprobamos que el formato recibido sea exactamente YYYY-MM-DD.
        if fecha_validada.strftime("%Y-%m-%d") != fecha:
            return None, "El parámetro fecha debe tener el formato YYYY-MM-DD."

    except ValueError:
        return None, "El parámetro fecha debe tener el formato YYYY-MM-DD."

    return fecha, None


def validar_id_turno(valor):
    if valor is None:
        return None, "Debe proporcionar el id_turno."

    try:
        id_turno = int(valor)
    except (ValueError, TypeError):
        return None, "El id_turno debe ser un número entero válido."

    if id_turno <= 0:
        return None, "El id_turno debe ser un entero positivo."

    return id_turno, None