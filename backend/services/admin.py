from repositories.admin import (listar_catalogo, obtener_catalogo, crear_catalogo, actualizar_catalogo, eliminar_catalogo, contar_medicos, contar_especialidades, contar_pacientes, contar_turnos_hoy)


def listar(resource):
    return listar_catalogo(resource)


def obtener(resource, item_id):
    item = obtener_catalogo(resource, item_id)
    if item is None:
        raise LookupError('No se encontró el recurso solicitado')
    return item


def crear(resource, values):
    item_id = crear_catalogo  (resource, values)
    return obtener(resource, item_id)


def actualizar(resource, item_id, values):
    obtener(resource, item_id)
    actualizar_catalogo(resource, item_id, values)
    return obtener(resource, item_id)


def eliminar(resource, item_id):
    obtener(resource, item_id)
    eliminar_catalogo(resource, item_id)

def resumen():
    return {
        "medicos": contar_medicos(),
        "especialidades": contar_especialidades(),
        "pacientes": contar_pacientes(),
        "turnos_hoy": contar_turnos_hoy()
    }