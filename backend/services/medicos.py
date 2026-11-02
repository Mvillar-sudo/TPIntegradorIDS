from ..repositories import medicos


def listar(especialidad_id=None):
    return medicos.listar_medicos(especialidad_id)


def obtener(medico_id):
    item = medicos.obtener_medico(medico_id)
    if item is None:
        raise LookupError('No se encontró el médico solicitado')
    return item


def crear(values):
    if not medicos.especialidad_existe(values['id_especialidad']):
        raise ValueError('La especialidad indicada no existe')
    if medicos.matricula_existe(values['matricula']):
        raise ValueError('La matrícula ingresada ya existe')
    return medicos.crear(values)


def actualizar(medico_id, values):
    obtener(medico_id)
    if 'id_especialidad' in values and not medicos.especialidad_existe(values['id_especialidad']):
        raise ValueError('La especialidad indicada no existe')
    if 'matricula' in values and medicos.matricula_existe(values['matricula'], medico_id):
        raise ValueError('La matrícula ingresada ya existe')
    medicos.actualizar_medico(medico_id, values)
    return obtener(medico_id)


def eliminar(medico_id):
    obtener(medico_id)
    if medicos.tiene_dependencias(medico_id):
        raise ValueError('No se puede eliminar un médico con agendas o turnos asociados')
    medicos.eliminar_medico(medico_id)