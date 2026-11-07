from mysql.connector import Error, IntegrityError, errorcode
from werkzeug.security import generate_password_hash

from repositories.usuarios_repositories import (
    obtener_usuario_por_email, obtener_usuario_por_dni, crear_usuario
)
from validators.validator_auth import validar_registro


def registrar_usuario(datos, rol):
    """
    Pre: 'datos' es el cuerpo JSON del pedido (puede no ser un diccionario) y 'rol' es el rol
         con el que se crea el usuario ('paciente', 'recepcionista' o 'medico').
    Post: Devuelve (usuario, None, None) si lo creó, donde 'usuario' es un diccionario con
          id_usuario, nombre, apellido, email y rol. Si no pudo, devuelve (None, mensaje, codigo)
          con el mensaje de error y el código HTTP que corresponde.
    """
    valido, error = validar_registro(datos)
    if not valido:
        return None, error, 400

    nombre = datos["nombre"].strip()
    apellido = datos["apellido"].strip()
    dni = datos["dni"].strip()
    email = datos["email"].strip().lower()
    telefono = (datos.get("telefono") or "").strip() or None
    id_cobertura = datos.get("id_cobertura")

    try:
        if obtener_usuario_por_email(email):
            return None, "El email ya está registrado", 409

        if obtener_usuario_por_dni(dni):
            return None, "El DNI ya está registrado", 409

        password_hash = generate_password_hash(datos["password"])

        id_usuario = crear_usuario(
            nombre, apellido, dni, email, password_hash, telefono, id_cobertura, rol
        )

    except IntegrityError as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            return None, "El email o el DNI ya están registrados", 409
        if err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            return None, "La cobertura indicada no existe", 400
        return None, "No se pudo registrar el usuario", 500

    except Error:
        return None, "No se pudo registrar el usuario", 500

    usuario = {
        "id_usuario": id_usuario, "nombre": nombre, "apellido": apellido,
        "email": email, "rol": rol
    }
    return usuario, None, None
