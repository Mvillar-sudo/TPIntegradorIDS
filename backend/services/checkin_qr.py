from datetime import datetime, timezone, timedelta

try:
    from repositories.checkin_qr import (
        buscar_turno_por_qr,
        confirmar_checkin_turno,
        actualizar_turno_a_ausente,
    )
except ImportError:
    from backend.repositories.checkin_qr import (
        buscar_turno_por_qr,
        confirmar_checkin_turno,
        actualizar_turno_a_ausente,
    )

"""
Pre: -
Post: Devuelve la fecha y hora actual en GMT-3 para comparar con el campo DATETIME de MySQL.
"""
def obtener_ahora_gmt3():
    zona_gmt3 = timezone(timedelta(hours=-3))
    return datetime.now(zona_gmt3).replace(tzinfo=None, microsecond=0)

"""
Pre: 'dt' es un objeto datetime o None
Post: Formatea 'dt' como 'YYYY-MM-DDTHH:MM:SS'.
"""
def formatear_fecha_iso(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")

"""
Pre: 'codigo_qr_hash' es un string no vacío.
Post: Registra el check-in del turno correspondiente al código QR, siguiendo las reglas de negocio.
"""
def registrar_checkin_por_qr(codigo_qr_hash):
    turno = buscar_turno_por_qr(codigo_qr_hash)

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
    fecha_inicio = turno["fecha_hora_inicio"].replace(tzinfo=None)

    inicio_ventana = fecha_inicio - timedelta(minutes=30)
    fin_ventana = fecha_inicio + timedelta(minutes=15)

    if ahora < inicio_ventana:
        return {
            "error": "Aún no se encuentra habilitada la ventana de check-in (30 minutos antes del turno)"
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

    return {
        "id_turno": turno["id_turno"],
        "estado": "confirmado",
        "fecha_hora_checkin": formatear_fecha_iso(ahora),
        "paciente": nombre_paciente,
    }, 200