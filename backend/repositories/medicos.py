from repositories.consultas_repositories import ejecutar_consulta
from constants import MEDICOS_BASE_SELECT
from tiempo import obtener_ahora_gmt3


def listar_medicos(especialidad_id=None):
    hoy = obtener_ahora_gmt3().date()
    query = MEDICOS_BASE_SELECT
    params = [hoy]
    if especialidad_id is not None:
        query += ' WHERE m.id_especialidad = %s'
        params.append(especialidad_id)
    query += ' ORDER BY u.apellido_usuario, u.nombre_usuario, m.id_medico'
    return ejecutar_consulta(query, tuple(params))


def obtener_medico(medico_id):
    hoy = obtener_ahora_gmt3().date()
    rows = ejecutar_consulta(MEDICOS_BASE_SELECT + ' WHERE m.id_medico = %s', (hoy, medico_id))
    return rows[0] if rows else None


def especialidad_existe(specialty_id):
    rows = ejecutar_consulta(
        'SELECT id_especialidad FROM especialidades WHERE id_especialidad = %s',
        (specialty_id,),
    )
    return bool(rows)


def matricula_existe(matricula, excluding=None):
    query = 'SELECT id_medico FROM medicos WHERE matricula = %s'
    params = [matricula]
    if excluding is not None:
        query += ' AND id_medico <> %s'
        params.append(excluding)
    return bool(ejecutar_consulta(query, tuple(params)))


def usuario_es_medico(usuario_id):
    rows = ejecutar_consulta(
        "SELECT id_usuario FROM usuarios WHERE id_usuario = %s AND rol_usuario = 'medico'",
        (usuario_id,),
    )
    return bool(rows)


def usuario_tiene_perfil_medico(usuario_id):
    rows = ejecutar_consulta(
        'SELECT id_medico FROM medicos WHERE id_usuario = %s',
        (usuario_id,),
    )
    return bool(rows)


def crear_medico(values):
    return ejecutar_consulta(
        'INSERT INTO medicos (id_usuario, id_especialidad, matricula) '
        'VALUES (%s, %s, %s)',
        (values['id_usuario'], values['id_especialidad'], values['matricula']),
    )


COLUMNAS_EDITABLES = {
    'id_especialidad': 'm.id_especialidad',
    'matricula': 'm.matricula',
    'nombre': 'u.nombre_usuario',
    'apellido': 'u.apellido_usuario',
    'dni': 'u.dni_usuario',
    'email': 'u.email_usuario',
    'telefono': 'u.telefono_usuario',
}


def dni_existe(dni, excluding_usuario=None):
    query = 'SELECT id_usuario FROM usuarios WHERE dni_usuario = %s'
    params = [dni]
    if excluding_usuario is not None:
        query += ' AND id_usuario <> %s'
        params.append(excluding_usuario)
    return bool(ejecutar_consulta(query, tuple(params)))


def email_existe(email, excluding_usuario=None):
    query = 'SELECT id_usuario FROM usuarios WHERE email_usuario = %s'
    params = [email]
    if excluding_usuario is not None:
        query += ' AND id_usuario <> %s'
        params.append(excluding_usuario)
    return bool(ejecutar_consulta(query, tuple(params)))


def actualizar_medico(medico_id, values):
    # Una sola sentencia sobre medicos y usuarios: o se guarda todo o no se guarda nada
    assignments = ', '.join(f'{COLUMNAS_EDITABLES[campo]} = %s' for campo in values)
    ejecutar_consulta(
        'UPDATE medicos AS m JOIN usuarios AS u ON u.id_usuario = m.id_usuario '
        f'SET {assignments} WHERE m.id_medico = %s',
        (*values.values(), medico_id),
    )


def tiene_dependencias(medico_id):
    rows = ejecutar_consulta(
        "SELECT 1 FROM agendas WHERE id_medico = %s UNION ALL "
        'SELECT 1 FROM turnos WHERE id_medico = %s LIMIT 1',
        (medico_id, medico_id),
    )
    return bool(rows)


def eliminar(medico_id):
    # Borra el perfil y también el usuario del médico, para que no pueda seguir iniciando sesión
    ejecutar_consulta(
        'DELETE m, u FROM medicos AS m JOIN usuarios AS u ON u.id_usuario = m.id_usuario '
        'WHERE m.id_medico = %s',
        (medico_id,),
    )