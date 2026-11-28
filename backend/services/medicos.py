from repositories import medicos


def listar(especialidad_id=None):
    return medicos.listar_medicos(especialidad_id)


def obtener(medico_id):
    item = medicos.obtener_medico(medico_id)
    if item is None:
        raise LookupError('No se encontró el médico solicitado')
    return item


def matricula_disponible(matricula, medico_id=None):
    """True si ninguna otra persona médica usa esa matrícula (la matrícula es única)."""
    return not medicos.matricula_existe(matricula, medico_id)


def crear(values):
    if not medicos.usuario_es_medico(values['id_usuario']):
        raise ValueError('El usuario indicado no existe o no tiene rol de médico')
    if medicos.usuario_tiene_perfil_medico(values['id_usuario']):
        raise ValueError('El usuario indicado ya está registrado como médico')
    if not medicos.especialidad_existe(values['id_especialidad']):
        raise ValueError('La especialidad indicada no existe')
    if medicos.matricula_existe(values['matricula']):
        raise ValueError('La matrícula ingresada ya existe')
    return medicos.crear_medico(values)


def actualizar(medico_id, values):
    medico = obtener(medico_id)
    if 'id_especialidad' in values and not medicos.especialidad_existe(values['id_especialidad']):
        raise ValueError('La especialidad indicada no existe')
    if 'matricula' in values and medicos.matricula_existe(values['matricula'], medico_id):
        raise ValueError('La matrícula ingresada ya existe')
    if 'dni' in values and medicos.dni_existe(values['dni'], medico['id_usuario']):
        raise ValueError('El DNI ingresado ya está registrado')
    if 'email' in values and medicos.email_existe(values['email'], medico['id_usuario']):
        raise ValueError('El email ingresado ya está registrado')
    medicos.actualizar_medico(medico_id, values)
    return obtener(medico_id)


def eliminar(medico_id):
    obtener(medico_id)
    if medicos.tiene_dependencias(medico_id):
        raise ValueError('No se puede eliminar un médico con agendas o turnos asociados')
    medicos.eliminar(medico_id)