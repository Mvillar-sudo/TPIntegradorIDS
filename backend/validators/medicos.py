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