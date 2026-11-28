import jwt
from flask import request

from config import SECRET_KEY

def token_required(roles_permitidos=None):
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None, "Token no proporcionado", 401

    token = auth_header.split(" ")[1]

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    except jwt.ExpiredSignatureError:
        return None, "Token expirado", 401

    except jwt.InvalidTokenError:
        return None, "Token invalido", 401

    if roles_permitidos is not None:
        if data.get("rol_usuario") not in roles_permitidos:
            return None, "No tiene permisos para realizar esta operación.", 403

    return data, None, None

def validar_login(datos):
    if not isinstance(datos, dict):
        return False, "Se requiere un objeto JSON válido"

    email = datos.get("email")
    password = datos.get("password")

    if not isinstance(email, str) or not email.strip():
        return False, "El email es obligatorio"

    if not isinstance(password, str) or not password:
        return False, "La contraseña es obligatoria"

    return True, None

def es_email_valido(email):

    if email.count("@") != 1:
        return False

    if len(email.split()) != 1 or email != email.strip():
        return False

    usuario, dominio = email.split("@")

    if not usuario:
        return False

    if "." not in dominio or dominio.startswith(".") or dominio.endswith(".") or ".." in dominio:
        return False

    return True


def es_dni_valido(dni):
    return dni.isascii() and dni.isdigit() and 7 <= len(dni) <= 8


def es_telefono_valido(telefono):
    permitidos = "0123456789+()- "

    if not 6 <= len(telefono) <= 20:
        return False

    for caracter in telefono:
        if caracter not in permitidos:
            return False

    return True


def validar_registro(datos):
    if not isinstance(datos, dict):
        return False, "Se requiere un objeto JSON válido"

    for campo, maximo in (("nombre", 100), ("apellido", 100), ("email", 150)):
        valor = datos.get(campo)

      
        if not isinstance(valor, str) or not valor.strip():
            return False, f"El campo {campo} es obligatorio"

        if len(valor.strip()) > maximo:
            return False, f"El campo {campo} no puede superar los {maximo} caracteres"

    if not es_email_valido(datos["email"].strip()):
        return False, "El email no tiene un formato válido"
    
    dominio = datos["email"].strip().split("@")[1].lower()
    
    if dominio != "gmail.com":
        return False, "El email debe ser de dominio gmail.com"
    
    dni = datos.get("dni")
    if not isinstance(dni, str) or not es_dni_valido(dni.strip()):
        return False, "El DNI debe tener 7 u 8 dígitos numéricos"

    password = datos.get("password")
    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        return False, "La contraseña debe tener entre 8 y 128 caracteres"

    telefono = datos.get("telefono")
    if telefono not in (None, ""):
        if not isinstance(telefono, str) or not es_telefono_valido(telefono.strip()):
            return False, "El teléfono no es válido"


    id_cobertura = datos.get("id_cobertura")
    if id_cobertura is not None:
        if isinstance(id_cobertura, bool) or not isinstance(id_cobertura, int) or id_cobertura < 1:
            return False, "id_cobertura debe ser un número entero positivo"

    return True, None