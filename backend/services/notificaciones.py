import html
import logging
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

from config import obtener_configuracion_mail
from repositories.notificaciones_repositories import obtener_detalle_turno
from services.qr import generar_qr_png


def construir_url_cancelacion(id_turno):
    """
    Pre: 'id_turno' es un entero positivo.
    Post: Devuelve la URL del frontend desde la que el paciente puede cancelar el turno.
    """
    base = obtener_configuracion_mail()["url_frontend"]
    return f"{base}/turnos/{id_turno}/cancelar"


def describir_turno(turno):
    """
    Pre: 'turno' es el diccionario que devuelve obtener_detalle_turno().
    Post: Devuelve un diccionario con los datos del turno ya formateados como texto legible.
    """
    consultorio = f"Consultorio {turno['numero_consultorio']}"
    if turno["piso"]:
        consultorio += f" ({turno['piso']})"

    return {
        "paciente": f"{turno['paciente_nombre']} {turno['paciente_apellido']}",
        "medico": f"{turno['medico_nombre']} {turno['medico_apellido']}",
        "especialidad": turno["especialidad"],
        "fecha_hora": turno["fecha_hora"].strftime("%d/%m/%Y %H:%M"),
        "consultorio": consultorio,
    }


def armar_texto_plano(datos, url_cancelar):
    """
    Pre: 'datos' es el diccionario de describir_turno(); 'url_cancelar' es un string.
    Post: Devuelve el cuerpo del mail en texto plano (para clientes que no muestran HTML).
    """
    return (
        f"Hola {datos['paciente']}, tu turno quedó reservado.\n\n"
        f"Médico: {datos['medico']}\n"
        f"Especialidad: {datos['especialidad']}\n"
        f"Fecha y hora: {datos['fecha_hora']}\n"
        f"{datos['consultorio']}\n\n"
        "Presentá el código QR de este mail en recepción al llegar.\n"
        f"Si no podés asistir, cancelá el turno desde: {url_cancelar}\n"
    )


def armar_html(datos, url_cancelar, cid_qr):
    """
    Pre: 'datos' es el diccionario de describir_turno(); 'cid_qr' es el Content-ID de la imagen
         del QR sin los signos < >.
    Post: Devuelve el cuerpo del mail en HTML. Los datos se escapan porque el nombre lo escribe
          el usuario al registrarse.
    """
    d = {clave: html.escape(valor) for clave, valor in datos.items()}
    url = html.escape(url_cancelar, quote=True)
    estilo_boton = (
        "display:inline-block;padding:12px 24px;background:#c0392b;color:#ffffff;"
        "text-decoration:none;border-radius:6px;font-weight:bold;"
    )

    return f"""\
<div style="font-family:Arial,Helvetica,sans-serif;max-width:480px;margin:0 auto;color:#222;">
  <h2>Turno reservado</h2>
  <p>Hola {d['paciente']}, tu turno quedó reservado:</p>
  <p>
    <strong>Médico:</strong> {d['medico']}<br>
    <strong>Especialidad:</strong> {d['especialidad']}<br>
    <strong>Fecha y hora:</strong> {d['fecha_hora']}<br>
    <strong>Lugar:</strong> {d['consultorio']}
  </p>
  <p>Presentá este código QR en recepción al llegar:</p>
  <p><img src="cid:{cid_qr}" alt="Código QR del turno" width="220" height="220"></p>
  <p>Si no podés asistir:</p>
  <p><a href="{url}" style="{estilo_boton}">Cancelar turno</a></p>
</div>
"""


def armar_mail_confirmacion(turno):
    """
    Pre: 'turno' es el diccionario que devuelve obtener_detalle_turno() y tiene token_qr.
    Post: Devuelve un EmailMessage (texto plano + HTML con el QR embebido) listo para enviar.
    """
    datos = describir_turno(turno)
    url_cancelar = construir_url_cancelacion(turno["id_turno"])
    cid_qr = make_msgid(domain="centro-medico.local")

    mensaje = EmailMessage()
    mensaje["Subject"] = "Turno reservado - Centro Médico Salud Integral"
    mensaje["From"] = obtener_configuracion_mail()["remitente"]
    mensaje["To"] = turno["paciente_email"]
    mensaje.set_content(armar_texto_plano(datos, url_cancelar))
    mensaje.add_alternative(armar_html(datos, url_cancelar, cid_qr[1:-1]), subtype="html")
    mensaje.get_payload()[1].add_related(
        generar_qr_png(turno["token_qr"]), maintype="image", subtype="png", cid=cid_qr
    )
    return mensaje


def enviar_mail(mensaje):
    """
    Pre: 'mensaje' es un EmailMessage con From y To; SMTP_HOST, SMTP_PORT, SMTP_USER y
         SMTP_PASSWORD están definidos en el .env.
    Post: Envía el mensaje por SMTP con STARTTLS. Lanza OSError (o una subclase, como
          smtplib.SMTPException) si no se pudo enviar.
    """
    configuracion = obtener_configuracion_mail()

    with smtplib.SMTP(configuracion["host"], configuracion["puerto"], timeout=10) as servidor:
        servidor.starttls()
        servidor.login(configuracion["usuario"], configuracion["password"])
        servidor.send_message(mensaje)


def notificar_reserva(id_turno):
    """
    Pre: 'id_turno' es un entero positivo y el turno ya fue reservado (commit hecho).
    Post: Envía al paciente el mail de confirmación con el QR y el botón de cancelar.
          Devuelve True si el mail salió y False si falló. Nunca lanza por un problema de mail
          (SMTP caído, .env mal completado, etc.), para que un error de mail no responda 500
          sobre una reserva que ya quedó guardada.
    """
    try:
        turno = obtener_detalle_turno(id_turno)
        if turno is None:
            return False
        enviar_mail(armar_mail_confirmacion(turno))
        return True
    except Exception as error:  # cualquier falla del mail: la reserva ya está guardada
        logging.warning("No se pudo enviar el mail del turno %s: %s: %s", id_turno, type(error).__name__, error)
        return False
