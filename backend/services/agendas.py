from repositories import agendas
from services.checkin_qr import formatear_fecha_iso


def listar():
    resultado = agendas.listar_agendas()
    for agenda in resultado:
        agenda['agenda_fecha_hora_inicio'] = formatear_fecha_iso(agenda['agenda_fecha_hora_inicio'])
        agenda['agenda_fecha_hora_fin'] = formatear_fecha_iso(agenda['agenda_fecha_hora_fin'])
    return resultado


def crear(values):
    return agendas.crear_agenda(values)
