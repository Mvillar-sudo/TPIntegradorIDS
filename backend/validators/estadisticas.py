from datetime import datetime


def validar_fecha(valor, campo):
    try:
        fecha = datetime.strptime(valor, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        raise ValueError(f"El parámetro '{campo}' debe tener formato YYYY-MM-DD")

    return fecha


def validar_filtros_estadisticas(parametros):
    permitidos = {'desde', 'hasta'}
    no_permitidos = set(parametros.keys()) - permitidos

    if no_permitidos:
        raise ValueError(f"Parámetros no permitidos: {', '.join(sorted(no_permitidos))}")

    valores_desde = parametros.getlist('desde')
    valores_hasta = parametros.getlist('hasta')

    if len(valores_desde) != 1 or len(valores_hasta) != 1:
        raise ValueError("Debe indicar una sola vez los parámetros 'desde' y 'hasta'")

    desde = validar_fecha(parametros.get('desde'), 'desde')
    hasta = validar_fecha(parametros.get('hasta'), 'hasta')

    if desde > hasta:
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final")

    return desde, hasta