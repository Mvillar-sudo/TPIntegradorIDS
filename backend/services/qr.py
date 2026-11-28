import io

import qrcode
from qrcode.image.pure import PyPNGImage


def generar_qr_png(token_qr):
    """
    Pre: 'token_qr' es un string no vacío (el valor guardado en turnos.token_qr).
    Post: Devuelve los bytes de una imagen PNG con el código QR del token.
    """
    if not isinstance(token_qr, str) or not token_qr:
        raise ValueError("El token del QR es obligatorio")

    imagen = qrcode.make(token_qr, image_factory=PyPNGImage, box_size=8, border=2)
    buffer = io.BytesIO()
    imagen.save(buffer)
    return buffer.getvalue()
