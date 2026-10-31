"""
Pre: data es un diccionario que representa el cuerpo de la petición
Post: Valida que el body de POST /api/v1/turnos/checkin tenga exactamente el campo 'codigo_qr_hash' como string no vacío.
"""
def validar_entrada_checkin(data):
    if not isinstance(data, dict):
        raise ValueError("El cuerpo de la petición debe ser un objeto JSON válido")

    if set(data.keys()) != {"codigo_qr_hash"}:
        raise ValueError("El cuerpo debe contener únicamente el campo 'codigo_qr_hash'")

    codigo = data.get("codigo_qr_hash")
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("El campo 'codigo_qr_hash' debe ser una cadena de texto no vacía")

    codigo_limpio = codigo.strip()
    if len(codigo_limpio) > 255:
        raise ValueError("El campo 'codigo_qr_hash' no puede superar los 255 caracteres")

    return codigo_limpio