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
GESTION_ROLES = ('admin', 'recepcionista')
ROLES_PERSONAL_CREABLES = ('recepcionista', 'medico')

MIN_HORAS_CANCELACION = 2
ESTADOS_CON_QR = ('reservado', 'confirmado')
MAX_ESPACIOS_GENERADOS = 10000
MAX_DIAS_AGENDA = 365
MAX_DURACION_MINUTOS = 60

MEDICOS_BASE_SELECT = """
    SELECT m.id_medico, m.id_usuario, m.id_especialidad,
           u.nombre_usuario AS nombre_medico,
           u.apellido_usuario AS apellido_medico,
           u.dni_usuario AS dni_medico,
           u.email_usuario AS email_medico,
           u.telefono_usuario AS telefono_medico,
           m.matricula,
           e.nombre_especialidad AS especialidad,
           c.numero_consultorio,
           c.piso,
           CONCAT(
               c.numero_consultorio,
               IF(c.piso IS NOT NULL AND c.piso <> '', CONCAT(' (', c.piso, ')'), '')
           ) AS consultorio
    FROM medicos AS m
    JOIN usuarios AS u ON u.id_usuario = m.id_usuario
    JOIN especialidades AS e ON e.id_especialidad = m.id_especialidad
    LEFT JOIN consultorios AS c ON c.id_consultorio = COALESCE(
        (SELECT t1.id_consultorio
         FROM turnos t1
         WHERE t1.id_medico = m.id_medico AND DATE(t1.fecha_hora) = %s
         ORDER BY t1.fecha_hora ASC
         LIMIT 1),
        (SELECT a1.id_consultorio
         FROM agendas a1
         WHERE a1.id_medico = m.id_medico
         ORDER BY a1.agenda_fecha_hora_inicio DESC
         LIMIT 1),
        (SELECT t2.id_consultorio
         FROM turnos t2
         WHERE t2.id_medico = m.id_medico
         ORDER BY t2.fecha_hora DESC
         LIMIT 1)
    )
"""

MINUTOS_CHECKIN_ANTES = 30
MINUTOS_CHECKIN_DESPUES = 15
