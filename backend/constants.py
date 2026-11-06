import os

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
LECTORES_ROLES = ('admin', 'recepcionista', 'paciente', 'medico')
PERSONAL_ROLES = ('admin', 'recepcionista', 'medico')

MAX_ESPACIOS_GENERADOS = 10000
MAX_DIAS_AGENDA = 365
MAX_DURACION_MINUTOS = 60

MEDICOS_BASE_SELECT = """
    SELECT m.id_medico, m.id_especialidad,
           u.nombre_usuario AS nombre_medico,
           u.apellido_usuario AS apellido_medico, m.matricula,
           e.nombre_especialidad AS especialidad
    FROM medicos AS m
    JOIN usuarios AS u ON u.id_usuario = m.id_usuario
    JOIN especialidades AS e ON e.id_especialidad = m.id_especialidad
"""