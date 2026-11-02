from ..repositories import agendas


def listar():
    return agendas.listar_agendas()


def crear(values):
    return agendas.crear_agenda(values)