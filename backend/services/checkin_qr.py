from datetime import timedelta

from constants import MINUTOS_CHECKIN_ANTES, MINUTOS_CHECKIN_DESPUES
from tiempo import obtener_ahora_gmt3

try:
    from repositories.checkin_qr import (
        buscar_turno_por_qr,
        confirmar_checkin_turno,
        actualizar_turno_a_ausente,
        marcar_ausentes_vencidos,
    )
except ImportError:
    from backend.repositories.checkin_qr import (
        buscar_turno_por_qr,
        confirmar_checkin_turno,
        actualizar_turno_a_ausente,
        marcar_ausentes_vencidos,
    )
"""
Pre: 'dt' es un objeto datetime o None
Post: Formatea 'dt' como 'YYYY-MM-DDTHH:MM:SS'.
"""
def formatear_fecha_iso(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")

"""
Pre: 'token_qr' es un string no vacío.
Post: Registra el check-in del turno correspondiente al código QR, siguiendo las reglas de negocio.
"""
def registrar_checkin_por_qr(token_qr):
    turno = buscar_turno_por_qr(token_qr)

    if turno is None:
        return {"error": "Código QR inválido o turno no encontrado"}, 404

    estado_actual = turno["estado"]

    if estado_actual == "confirmado":
        return {"error": "El check-in para este turno ya fue realizado previamente"}, 400

    if estado_actual == "ausente":
        return {
            "error": "Turno fuera de la ventana horaria permitida para check-in. Marcado como ausente"
        }, 400

    if estado_actual != "reservado":
        return {
            "error": f"No se puede realizar el check-in de un turno en estado '{estado_actual}'"
        }, 400

    ahora = obtener_ahora_gmt3()
    fecha_turno = turno["fecha_hora"].replace(tzinfo=None)

    inicio_ventana = fecha_turno - timedelta(minutes=MINUTOS_CHECKIN_ANTES)
    fin_ventana = fecha_turno + timedelta(minutes=MINUTOS_CHECKIN_DESPUES)

    if ahora < inicio_ventana:
        return {
            "error": f"Aún no se encuentra habilitada la ventana de check-in ({MINUTOS_CHECKIN_ANTES} minutos antes del turno)"
        }, 400

    if ahora > fin_ventana:
        actualizar_turno_a_ausente(turno["id_turno"])
        return {
            "error": "Turno fuera de la ventana horaria permitida para check-in. Marcado como ausente"
        }, 400

    exito = confirmar_checkin_turno(turno["id_turno"], ahora)
    if not exito:
        return {"error": "No se pudo confirmar el check-in. El turno no se encuentra en estado reservado"}, 400

    nombre = turno.get("paciente_nombre") or ""
    apellido = turno.get("paciente_apellido") or ""
    nombre_paciente = f"{nombre} {apellido}".strip()

    medico_nom = f"{turno.get('medico_nombre', '')} {turno.get('medico_apellido', '')}".strip()
    medico = f"Dr. {medico_nom}" if medico_nom else "Profesional asignado"

    consultorio = str(turno.get("numero_consultorio") or "Consultorio asignado")

    return {
        "id_turno": turno["id_turno"],
        "estado": "confirmado",
        "fecha_hora": formatear_fecha_iso(fecha_turno),
        "fecha_hora_checkin": formatear_fecha_iso(ahora),
        "paciente": nombre_paciente,
        "medico": medico,
        "consultorio": consultorio,
    }, 200

"""
Pre: -
Post: Pasa a 'ausente' todos los turnos 'reservados' cuya ventana de check-in ya cerró, es decir,
      los que empezaron hace más de MINUTOS_CHECKIN_DESPUES minutos. Usa la hora de Argentina
      (obtener_ahora_gmt3). Devuelve la cantidad de turnos que marcó como ausentes.
"""
def marcar_ausentes():
    ahora = obtener_ahora_gmt3()
    limite = ahora - timedelta(minutes=MINUTOS_CHECKIN_DESPUES)
    return marcar_ausentes_vencidos(limite)