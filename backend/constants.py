import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'mailin2004'),
    'database': os.getenv('DB_NAME', 'centro_medico'),
}
SECRET_KEY = 'clave_secreta_jwt_salud_integral'

CATALOGO = {
    'especialidades': {
        'table': 'especialidades',
        'id': 'id_especialidad',
        'columns': ('nombre_especialidad',),
    },
    'consultorios': {
        'table': 'consultorios',
        'id': 'id_consultorio',
        'columns': ('numero_consultorio', 'piso'),
    },
    'coberturas': {
        'table': 'coberturas',
        'id': 'id_cobertura',
        'columns': ('nombre_cobertura',),
    },
}

CATALOGO_CAMPOS = {
    'especialidades': {'nombre': ('nombre_especialidad', 100)},
    'consultorios': {
        'numero_consultorio': ('numero_consultorio', 20),
        'piso': ('piso', 20),
    },
    'coberturas': {'nombre': ('nombre_cobertura', 100)},
}

ADMIN_ROLES = ('admin',)
LECTORES_ROLES = ('admin', 'recepcionista', 'paciente')
PERSONAL_ROLES = ('admin', 'recepcionista')

MAX_ESPACIOS_GENERADOS = 10000
MAX_DIAS_AGENDA = 365
MAX_DURACION_MINUTOS = 60

MEDICOS_BASE_SELECT = """
    SELECT m.id_medico, m.id_especialidad, m.nombre_medico,
           m.apellido_medico, m.matricula,
           e.nombre_especialidad AS especialidad
    FROM medicos AS m
    JOIN especialidades AS e ON e.id_especialidad = m.id_especialidad
"""