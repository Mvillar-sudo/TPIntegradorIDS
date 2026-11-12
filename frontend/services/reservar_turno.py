from services.api_client import pedir
from datetime import datetime, timedelta, timezone

"""
pre: -
post: consulta especialidades disponibles en la API y devuelve una tupla (especialidades, error, status).
"""
def listar_especialidades():
    return pedir("GET", "/especialidades")


def listar_medicos(id_especialidad):
    return pedir(
        "GET",
        "/medicos",
        params={"id_especialidad": id_especialidad},
    )

def obtener_medicos(id_especialidad):
    medicos, error, status = listar_medicos(id_especialidad)
    if error:
        return None, error, status
    return medicos or [], None, status

def listar_turnos_disponibles(medico_id, id_especialidad, fecha):
    return pedir(
        "GET",
        "/turnos/disponibles",
        params={
            "medico_id": medico_id,
            "id_especialidad": id_especialidad,
            "fecha": fecha,
        },
    )

def reservar_turno(id_turno):
    return pedir(
        "POST",
        "/turnos/reservar",
        json={"id_turno": id_turno},
    )

def fecha_minima():
    zona_gmt3 = timezone(timedelta(hours=-3))
    return (datetime.now(zona_gmt3).date() + timedelta(days=1)).isoformat()

def fecha_valida_para_busqueda(fecha):
    try:
        fecha_parseada = datetime.strptime(fecha, "%Y-%m-%d")
    except (TypeError, ValueError):
        return False
    return fecha_parseada.strftime("%Y-%m-%d") == fecha and fecha >= fecha_minima()