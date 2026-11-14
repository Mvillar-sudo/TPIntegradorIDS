import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")


def validar_configuracion():
    """
    Pre: el .env ya se cargó con load_dotenv().
    Post: Si falta alguna variable obligatoria, lanza RuntimeError con un mensaje que dice cuáles
          faltan. Si están todas, no hace nada.
    """
    obligatorias = ("JWT_SECRET_KEY", "DB_NAME", "DB_USER")
    faltantes = [nombre for nombre in obligatorias if not os.getenv(nombre)]

    if faltantes:
        raise RuntimeError(
            "Faltan variables en el archivo .env: " + ", ".join(faltantes)
            + ". Copiá .env.example como backend/.env y completalo."
        )


def obtener_configuracion_db():
    """
    Pre: -
    Post: Devuelve un diccionario con los datos de conexión a MySQL, listo para
          mysql.connector.connect(**diccionario).
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def obtener_configuracion_mail():
    """
    Pre: -
    Post: Devuelve un diccionario con los datos para enviar mails por SMTP: host, puerto, usuario,
          password, remitente (MAIL_FROM o, si no está, SMTP_USER) y url_frontend (sin barra final).
    """
    # Google muestra la contraseña de aplicación en grupos de 4 separados por espacios (a veces
    # espacios "raros" al copiar). Sin ningún espacio funciona igual y evita errores de codificación.
    return {
        "host": os.getenv("SMTP_HOST", "").strip(),
        "puerto": int(os.getenv("SMTP_PORT") or "587"),
        "usuario": os.getenv("SMTP_USER", "").strip(),
        "password": "".join(os.getenv("SMTP_PASSWORD", "").split()),
        "remitente": os.getenv("MAIL_FROM") or os.getenv("SMTP_USER") or "",
        "url_frontend": os.getenv("FRONTEND_URL", "http://127.0.0.1:3000").rstrip("/"),
    }
