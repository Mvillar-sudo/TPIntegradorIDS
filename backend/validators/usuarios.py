from constants import ROLES_PERSONAL_CREABLES


def validar_rol_personal(datos):
    """
    Pre: 'datos' es el cuerpo JSON del pedido (puede no ser un diccionario).
    Post: Devuelve (rol, None) si el rol es uno de los que el admin puede crear, o
          (None, mensaje) si falta o no es válido.
    """
    rol = datos.get("rol") if isinstance(datos, dict) else None

    if rol not in ROLES_PERSONAL_CREABLES:
        return None, "El rol debe ser uno de: " + ", ".join(ROLES_PERSONAL_CREABLES)

    return rol, None
