from datetime import timedelta

from repositories.estadisticas import obtener_ausentismo_por_especialidad, obtener_ocupacion_por_consultorio


def _porcentaje(parte, total):
    if total:
        resultado = round(parte / total * 100, 2) 
    else:
        resultado = 0.0

    return resultado


def obtener_estadisticas(desde, hasta):
    hasta_exclusivo = hasta + timedelta(days=1)
    ausentismo = obtener_ausentismo_por_especialidad(desde, hasta_exclusivo)
    ocupacion = obtener_ocupacion_por_consultorio(desde, hasta_exclusivo)

    for fila in ausentismo:
        ausentes = int(fila['turnos_ausentes'] or 0)
        atendidos = int(fila['turnos_atendidos'] or 0)
        fila['turnos_ausentes'] = ausentes
        fila['turnos_atendidos'] = atendidos
        fila['porcentaje_ausentismo'] = _porcentaje(ausentes, ausentes + atendidos)

    for fila in ocupacion:
        generados = int(fila['total_turnos_generados'] or 0)
        ocupados = int(fila['turnos_ocupados'] or 0)
        fila['total_turnos_generados'] = generados
        fila['turnos_ocupados'] = ocupados
        fila['porcentaje_ocupacion'] = _porcentaje(ocupados, generados)

    return {
        'periodo': {'desde': desde.isoformat(), 'hasta': hasta.isoformat()},
        'ausentismo_por_especialidad': ausentismo,
        'ocupacion_por_consultorio': ocupacion,
    }