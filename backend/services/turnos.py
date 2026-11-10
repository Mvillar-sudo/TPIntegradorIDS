from datetime import timedelta

from constants import ESTADOS_CON_QR, MIN_HORAS_CANCELACION
from repositories.medico import buscar_turno_por_id
from repositories.turnos_repositories import (
    registrar_cancelacion_turno, obtener_turnos_de_paciente
)
from services.checkin_qr import obtener_ahora_gmt3, formatear_fecha_iso
from services.qr import generar_qr_png


def _formatear_mi_turno(turno):
    """
    Pre: 'turno' es una fila de obtener_turnos_de_paciente().
    Post: Devuelve un diccionario con los datos del turno listos para la respuesta JSON.
    """
    consultorio = f"Consultorio {turno['numero_consultorio']}"
    if turno["piso"]:
        consultorio += f" ({turno['piso']})"

    return {
        "id_turno": turno["id_turno"],
        "fecha_hora": formatear_fecha_iso(turno["fecha_hora"]),
        "estado": turno["estado"],
        "medico": f"{turno['medico_nombre']} {turno['medico_apellido']}",
        "especialidad": turno["especialidad"],
        "consultorio": consultorio,
        "token_qr": turno["token_qr"],
    }


def listar_mis_turnos_servicio(id_paciente):
    """
    Pre: 'id_paciente' es el id_usuario de un paciente (entero positivo).
    Post: Devuelve una tupla (lista_json, status_code) con los turnos del paciente.
    """
    turnos = obtener_turnos_de_paciente(id_paciente)
    return [_formatear_mi_turno(turno) for turno in turnos], 200


def cancelar_turno_servicio(usuario, id_turno):
    """
    Pre: 'usuario' es el contenido del token (con id_usuario y rol_usuario) e 'id_turno' es un
         entero positivo.
    Post: Cancela el turno si corresponde y devuelve una tupla (respuesta_json, status_code).
          El paciente solo puede cancelar sus propios turnos reservados y hasta
          MIN_HORAS_CANCELACION horas antes. El admin puede cancelar cualquier turno reservado,
          sin el límite de horas.
    """
    turno = buscar_turno_por_id(id_turno)

    if turno is None:
        return {"error": "Turno no encontrado"}, 404

    es_admin = usuario["rol_usuario"] == "admin"

    if not es_admin and turno["id_paciente"] != usuario["id_usuario"]:
        return {"error": "El turno no pertenece al paciente autenticado"}, 403

    if turno["estado"] != "reservado":
        return {
            "error": f"No se puede cancelar un turno en estado '{turno['estado']}'. "
                     "Solo se pueden cancelar turnos reservados"
        }, 400

    ahora = obtener_ahora_gmt3()
    fecha_turno = turno["fecha_hora"].replace(tzinfo=None)

    if not es_admin and fecha_turno - ahora < timedelta(hours=MIN_HORAS_CANCELACION):
        return {
            "error": f"No se puede cancelar el turno si faltan menos de {MIN_HORAS_CANCELACION} horas"
        }, 400

    if not registrar_cancelacion_turno(id_turno, ahora):
        return {"error": "No se pudo cancelar el turno: ya no se encuentra reservado"}, 409

    return {
        "id_turno": id_turno,
        "estado": "cancelado",
        "fecha_hora_cancelacion": formatear_fecha_iso(ahora),
        "mensaje": "Turno cancelado con éxito"
    }, 200


def obtener_qr_turno_servicio(usuario, id_turno):
    """
    Pre: 'usuario' es el contenido del token (con id_usuario) e 'id_turno' es un entero positivo.
    Post: Devuelve una tupla (png, error, status). Si el turno es del paciente y sigue vigente
          (reservado o confirmado), 'png' son los bytes de la imagen del QR y 'error' es None.
          Si no, 'png' es None y 'error' explica el motivo.
    """
    turno = buscar_turno_por_id(id_turno)

    if turno is None:
        return None, "Turno no encontrado", 404

    if turno["id_paciente"] != usuario["id_usuario"]:
        return None, "El turno no pertenece al paciente autenticado", 403

    if turno["estado"] not in ESTADOS_CON_QR:
        return None, f"El turno está en estado '{turno['estado']}' y ya no tiene un QR vigente", 400

    return generar_qr_png(turno["token_qr"]), None, 200
