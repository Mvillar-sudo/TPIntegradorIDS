"""
Pre: 'data' es un diccionario que representa el cuerpo de la petición.
Post: Valida que el body de POST /api/v1/turnos/checkin contenga el campo 'token_qr' como string no vacío menor o igual a 255 caracteres.
"""
def validar_entrada_checkin(data):
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la petición debe ser un objeto JSON válido")

    campo = "token_qr" if "token_qr" in data else None
    if campo is None or len(data) != 1:
        raise ValueError("El cuerpo debe contener únicamente el campo 'token_qr'")

    codigo = data.get(campo)
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError(f"El campo '{campo}' debe ser una cadena de texto no vacía")

    codigo_limpio = codigo.strip()
    if len(codigo_limpio) > 255:
        raise ValueError(f"El campo '{campo}' no puede superar los 255 caracteres")

    return codigo_limpio
