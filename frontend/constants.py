import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:5000/api/v1')
FRONTEND_SECRET_KEY = os.getenv('FRONTEND_SECRET_KEY', 'clave_secreta_mockup_centro_medico')

RUTA_POR_ROL = {
    'admin': 'admin.dashboard',
    'recepcionista': 'recepcion.pantalla_recepcion',
    'medico': 'medico.agenda',
    'paciente': 'index',
}