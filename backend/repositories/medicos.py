from .consultas_repositories import ejecutar_consulta
from ..constants import MEDICOS_BASE_SELECT


def listar_medicos(especialidad_id=None):
    query = MEDICOS_BASE_SELECT
    params = ()
    if especialidad_id is not None:
        query += ' WHERE m.id_especialidad = %s'
        params = (especialidad_id,)
    query += ' ORDER BY m.apellido_medico, m.nombre_medico, m.id_medico'
    return ejecutar_consulta(query, params)


def obtener_medico(medico_id):
    rows = ejecutar_consulta(MEDICOS_BASE_SELECT + ' WHERE m.id_medico = %s', (medico_id,))
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


def crear_medico(values):
    return ejecutar_consulta(
        'INSERT INTO medicos '
        '(id_especialidad, nombre_medico, apellido_medico, matricula) '
        'VALUES (%s, %s, %s, %s)',
        (
            values['id_especialidad'], values['nombre_medico'],
            values['apellido_medico'], values['matricula'],
        ),
    )


def actualizar_medico(medico_id, values):
    assignments = ', '.join(f'{column} = %s' for column in values)
    ejecutar_consulta(
        f'UPDATE medicos SET {assignments} WHERE id_medico = %s',
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
    ejecutar_consulta('DELETE FROM medicos WHERE id_medico = %s', (medico_id,))