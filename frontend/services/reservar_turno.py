from services.api_client import pedir


def listar_especialidades():
    return pedir("GET", "/especialidades")


def listar_medicos(id_especialidad):
    return pedir(
        "GET",
        "/medicos",
        params={"id_especialidad": id_especialidad},
    )


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