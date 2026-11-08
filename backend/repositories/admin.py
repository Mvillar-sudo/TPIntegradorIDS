from repositories.consultas_repositories import ejecutar_consulta
from constants import CATALOGO


def _contar(query, params=None):
    return ejecutar_consulta(query, params, fetch_all=False)["total"]


def listar_catalogo(resource):
    spec = CATALOGO[resource]
    columns = ', '.join((spec['id'], *spec['columns']))
    return ejecutar_consulta(f"SELECT {columns} FROM {spec['table']} ORDER BY {spec['id']}")


def obtener_catalogo(resource, item_id):
    spec = CATALOGO[resource]
    columns = ', '.join((spec['id'], *spec['columns']))
    rows = ejecutar_consulta(
        f"SELECT {columns} FROM {spec['table']} WHERE {spec['id']} = %s",
        (item_id,),
    )
    if rows:
        return rows[0]
    else:
        return None


def crear_catalogo(resource, values):
    spec = CATALOGO[resource]
    columns = tuple(values)
    placeholders = ', '.join(['%s'] * len(columns))
    result = ejecutar_consulta(
        f"INSERT INTO {spec['table']} ({', '.join(columns)}) VALUES ({placeholders})",
        tuple(values[column] for column in columns),
    )
    return result


def actualizar_catalogo(resource, item_id, values):
    spec = CATALOGO[resource]
    columns = tuple(values)
    assignments = ', '.join(f'{column} = %s' for column in columns)
    ejecutar_consulta(
        f"UPDATE {spec['table']} SET {assignments} WHERE {spec['id']} = %s",
        (*[values[column] for column in columns], item_id),
    )


def eliminar_catalogo(resource, item_id):
    spec = CATALOGO[resource]
    ejecutar_consulta(
        f"DELETE FROM {spec['table']} WHERE {spec['id']} = %s",
        (item_id,),
    )


def contar_medicos():
    return _contar("SELECT COUNT(*) AS total FROM medicos")

def contar_especialidades():
    return _contar("SELECT COUNT(*) AS total FROM especialidades")

def contar_pacientes():
    return _contar("SELECT COUNT(*) AS total FROM usuarios WHERE rol_usuario = %s", ('paciente',),)

def contar_turnos_hoy():
    return _contar("SELECT COUNT(*) AS total FROM turnos WHERE DATE(fecha_hora) = CURDATE()")