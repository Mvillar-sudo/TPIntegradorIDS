from repositories import admin


def listar(resource):
    return admin.listar_catalogo(resource)


def obtener(resource, item_id):
    item = admin.obtener_catalogo(resource, item_id)
    if item is None:
        raise LookupError('No se encontró el recurso solicitado')
    return item


def crear(resource, values):
    item_id = admin.crear_catalogo  (resource, values)
    return obtener(resource, item_id)


def actualizar(resource, item_id, values):
    obtener(resource, item_id)
    admin.actualizar_catalogo(resource, item_id, values)
    return obtener(resource, item_id)


def eliminar(resource, item_id):
    obtener(resource, item_id)
    admin.eliminar_catalogo(resource, item_id)