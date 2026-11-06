from constants import CATALOGO_CAMPOS
from utils import validar_objeto_json, validar_texto


def validar_catalogo(resource, body, partial=False):
    body = validar_objeto_json(body)
    fields = CATALOGO_CAMPOS[resource]
    unknown = set(body) - set(fields)
    if unknown:
        raise ValueError(f"Campos no permitidos: {', '.join(sorted(unknown))}")
    if not body and partial:
        raise ValueError('Debe indicar al menos un campo para actualizar')

    result = {}
    for api_field, (db_field, max_length) in fields.items():
        if api_field in body:
            value = body[api_field]
            if resource == 'consultorios' and api_field == 'piso' and value is None:
                result[db_field] = None
            else:
                result[db_field] = validar_texto(value, api_field, max_length)
        elif not partial and not (resource == 'consultorios' and api_field == 'piso'):
            raise ValueError(f"El campo '{api_field}' es obligatorio")
    return result