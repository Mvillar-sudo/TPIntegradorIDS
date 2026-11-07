from utils import validar_entero_positivo, validar_objeto_json, validar_texto


def validar_medico(body, partial=False):
    body = validar_objeto_json(body)
    fields = {'id_especialidad', 'matricula'}
    if not partial:
        fields.add('id_usuario')
    unknown = set(body) - fields
    if unknown:
        raise ValueError(f"Campos no permitidos: {', '.join(sorted(unknown))}")
    if not body and partial:
        raise ValueError('Debe indicar al menos un campo para actualizar')

    result = {}
    if 'id_usuario' in body:
        result['id_usuario'] = validar_entero_positivo(body['id_usuario'], 'id_usuario')
    elif not partial:
        raise ValueError("El campo 'id_usuario' es obligatorio")
    if 'id_especialidad' in body:
        result['id_especialidad'] = validar_entero_positivo(body['id_especialidad'], 'id_especialidad')
    elif not partial:
        raise ValueError("El campo 'id_especialidad' es obligatorio")
    if 'matricula' in body:
        result['matricula'] = validar_texto(body['matricula'], 'matricula', 50)
    elif not partial:
        raise ValueError("El campo 'matricula' es obligatorio")
    return result


def validar_id_turno(id_turno):
    """
    Pre: 'id_turno' es un entero o string representable como entero.
    Post: Valida que 'id_turno' sea un entero positivo mayor a cero y lo devuelve como int.
    """
    if id_turno is None:
        raise ValueError("El identificador del turno es obligatorio")

    try:
        id_int = int(id_turno)
    except (ValueError, TypeError):
        raise ValueError("El identificador del turno debe ser un número entero válido")

    if id_int <= 0:
        raise ValueError("El identificador del turno debe ser un entero positivo")

    return id_int


def validar_especialidad_id(valor):
    """
    Pre: 'valor' es un entero, string numérico o None.
    Post: Devuelve (especialidad_id, error). Si es None devuelve (None, None).
    """
    if valor is None:
        return None, None

    try:
        especialidad_id = int(valor)
    except ValueError:
        return None, "El parámetro especialidad_id debe ser un número entero válido."

    if especialidad_id <= 0:
        return None, "El parámetro especialidad_id debe ser un entero positivo."

    return especialidad_id, None
