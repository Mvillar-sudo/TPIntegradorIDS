from flask import jsonify
from mysql.connector import Error
from datetime import datetime, timedelta

def respuesta_error(error):
    if isinstance(error, LookupError):
        return jsonify({'error': str(error)}), 404
    if isinstance(error, ValueError):
        return jsonify({'error': str(error)}), 400
    if isinstance(error, Error):
        if error.errno == 1062:
            return jsonify({'error': 'El DNI, email o matrícula ingresado ya está registrado'}), 409
        if error.errno == 1451:
            return jsonify({'error': 'No se puede eliminar el recurso porque tiene datos asociados'}), 409
        if error.errno == 1452:
            return jsonify({'error': 'Una de las referencias indicadas no existe'}), 400
        return jsonify({'error': 'No se pudo completar la operación de base de datos'}), 503
    return jsonify({'error': 'Error interno del servidor'}), 500


def validar_texto(value, field, max_length):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"El campo '{field}' es obligatorio")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"El campo '{field}' supera los {max_length} caracteres")
    return value


def validar_entero_positivo(value, field):
    if isinstance(value, bool):
        raise ValueError(f"El campo '{field}' debe ser un entero positivo")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and value.strip().isdigit():
        result = int(value.strip())
    else:
        raise ValueError(f"El campo '{field}' debe ser un entero positivo") from None
    if result < 1:
        raise ValueError(f"El campo '{field}' debe ser un entero positivo")
    return result


def validar_objeto_json(body):
    if not isinstance(body, dict):
        raise ValueError('El cuerpo debe ser un objeto JSON')
    return body

def generar_intervalos_turnos(fecha_str, hora_inicio_str, hora_fin_str):
    formato = "%Y-%m-%d %H:%M:%S"
    inicio_dt = datetime.strptime(f"{fecha_str} {hora_inicio_str}", formato)
    fin_dt = datetime.strptime(f"{fecha_str} {hora_fin_str}", formato)
    turnos = []
    turno_actual = inicio_dt 
    while turno_actual + timedelta(hours=1) <= fin_dt:
        turnos.append(turno_actual)
        turno_actual += timedelta(hours=1)
    return turnos