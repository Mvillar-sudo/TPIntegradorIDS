from utils import validar_entero_positivo, validar_objeto_json, validar_texto
from validators.validator_auth import es_dni_valido, es_email_valido, es_telefono_valido

DOMINIO_EMAIL_PERMITIDO = 'gmail.com'


def _validar_dni(value):
    if not isinstance(value, str) or not es_dni_valido(value.strip()):
        raise ValueError('El DNI debe tener 7 u 8 dígitos numéricos')
    return value.strip()


def _validar_email(value):
    texto = validar_texto(value, 'email', 150).lower()
    if not es_email_valido(texto):
        raise ValueError('El email no tiene un formato válido')
    if texto.split('@')[1] != DOMINIO_EMAIL_PERMITIDO:
        raise ValueError(f'El email debe ser de dominio {DOMINIO_EMAIL_PERMITIDO}')
    return texto


def _validar_telefono(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str) or not es_telefono_valido(value.strip()):
        raise ValueError('El teléfono no es válido')
    return value.strip()


def validar_medico(body, partial=False):
    body = validar_objeto_json(body)
    fields = {'id_especialidad', 'matricula'}
    if partial:
        # Al modificar también se pueden cambiar los datos personales del usuario del médico
        fields |= {'nombre', 'apellido', 'dni', 'email', 'telefono'}
    else:
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
    if 'nombre' in body:
        result['nombre'] = validar_texto(body['nombre'], 'nombre', 100)
    if 'apellido' in body:
        result['apellido'] = validar_texto(body['apellido'], 'apellido', 100)
    if 'dni' in body:
        result['dni'] = _validar_dni(body['dni'])
    if 'email' in body:
        result['email'] = _validar_email(body['email'])
    if 'telefono' in body:
        result['telefono'] = _validar_telefono(body['telefono'])
    return result
