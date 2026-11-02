"""
Pre: 'id_turno' es un entero.
Post: Valida que 'id_turno' sea un número entero positivo mayor a cero y lo devuelve como int.
"""
def validar_id_turno(id_turno):
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
    if valor is None:
        return None, None

    try:
        especialidad_id = int(valor)
    except ValueError:
        return None, "El parámetro especialidad_id debe ser un número entero válido."

    if especialidad_id <= 0:
        return None, "El parámetro especialidad_id debe ser un entero positivo."

    return especialidad_id, None
