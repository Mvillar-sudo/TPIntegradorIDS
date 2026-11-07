import uuid
import hashlib
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from repositories.especialidades_repositories import obtener_especialidades
from repositories.turnos_repositories import (obtener_turnos_disponibles, reservar_turno)

from validators.turnos_validator import (validar_id_opcional,validar_fecha_opcional, validar_id_turno)
from validators.validator_auth import token_required

turnos_bp = Blueprint('turnos', __name__)


@turnos_bp.route('/turnos/mis-turnos', methods=['GET'])
@token_required()
def obtener_mis_turnos():
    usuario = request.user_data
    id_usuario = usuario.get("id_usuario") or usuario.get("id")
    
    return jsonify({
        "status": "success",
        "mensaje": f"Lista de turnos para el usuario {id_usuario}"
    }), 200


@turnos_bp.route('/turnos/<int:id_turno>/cancelar', methods=['POST'])
@token_required()
def cancelar_turno(id_turno):
    fecha_turno_simulada = datetime.now() + timedelta(hours=5) 
    
    ahora = datetime.now()
    
    diferencia = fecha_turno_simulada - ahora
    
    
    if diferencia.total_seconds() < 7200:
        return jsonify({
            "status": "error",
            "error": "No se puede cancelar el turno si faltan menos de 2 horas."
        }), 400
        
    
    return jsonify({
        "status": "success",
        "mensaje": f"El turno {id_turno} fue cancelado exitosamente."
    }), 200

@turnos_bp.route("/especialidades", methods=["GET"])
def listar_especialidades():
    resultados = obtener_especialidades()

    if resultados is None:
        return jsonify({
            "error": "No se pudieron obtener las especialidades."
        }), 500

    especialidades = [
        {
            "id_especialidad": row["id_especialidad"],
            "nombre": row["nombre_especialidad"]
        }
        for row in resultados
    ]

    return jsonify(especialidades), 200


@turnos_bp.route("/turnos/disponibles", methods=["GET"])
def listar_turnos_disponibles():
    medico_id_recibido = request.args.get("medico_id")
    especialidad_id_recibido = request.args.get("especialidad_id")
    fecha_recibida = request.args.get("fecha")

    # Validar medico_id
    medico_id, error = validar_id_opcional(
        medico_id_recibido,
        "medico_id"
    )

    if error is not None:
        return jsonify({"error": error}), 400

    # Validar especialidad_id
    especialidad_id, error = validar_id_opcional(
        especialidad_id_recibido,
        "especialidad_id"
    )

    if error is not None:
        return jsonify({"error": error}), 400

    # Validar fecha
    fecha, error = validar_fecha_opcional(fecha_recibida)

    if error is not None:
        return jsonify({"error": error}), 400

    # Consultar el repository
    resultados = obtener_turnos_disponibles(
        medico_id=medico_id,
        fecha=fecha,
        especialidad_id=especialidad_id
    )

    if resultados is None:
        return jsonify({
            "error": "No se pudieron obtener los turnos disponibles."
        }), 500

    # Preparar la respuesta JSON
    turnos_disponibles = []

    for row in resultados:
        fecha_hora = row["fecha_hora"]

        if hasattr(fecha_hora, "strftime"):
            fecha_hora = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        else:
            fecha_hora = str(fecha_hora)

        turnos_disponibles.append({
            "id_turno": row["id_turno"],
            "id_medico": row["id_medico"],
            "medico": f"{row['nombre_medico']} {row['apellido_medico']}",
            "id_especialidad": row["id_especialidad"],
            "especialidad": row["nombre_especialidad"],
            "id_consultorio": row["id_consultorio"],
            "consultorio": (
                f"Consultorio {row['numero_consultorio']} "
                f"({row['piso']})"
            ),
            "fecha_hora": fecha_hora,
            "estado": row["estado"]
        })

    return jsonify(turnos_disponibles), 200

@turnos_bp.route("/turnos/reservar", methods=["POST"])
@token_required()
def reservar_turno_endpoint():
    # 1. Obtener el usuario autenticado desde el token.
    user_data = getattr(request, "user_data", {})
    id_paciente = user_data.get("id_usuario")

    if not id_paciente:
        return jsonify({
            "error": "El token no contiene un id_usuario válido."
        }), 401

    # 2. Obtener y validar el cuerpo de la petición.
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "id_turno" not in data:
        return jsonify({
            "error": "Debe proporcionar el id_turno en el cuerpo de la petición."
        }), 400

    id_turno, error = validar_id_turno(data["id_turno"])

    if error is not None:
        return jsonify({"error": error}), 400

    # 3. Generar el hash que se utilizará como token del QR.
    semilla = (
        f"TURNO-{id_turno}-PACIENTE-{id_paciente}-"
        f"{datetime.now().isoformat()}-{uuid.uuid4().hex}"
    )

    codigo_qr_hash = hashlib.sha256(
        semilla.encode("utf-8")
    ).hexdigest()

    # 4. Intentar realizar la reserva.
    resultado = reservar_turno(
        id_turno=id_turno,
        id_paciente=id_paciente,
        codigo_qr_hash=codigo_qr_hash
    )

    estado = resultado["estado"]

    if estado == "no_encontrado":
        return jsonify({
            "error": "El turno solicitado no existe."
        }), 404

    if estado == "no_disponible":
        return jsonify({
            "error": "El turno ya no se encuentra disponible."
        }), 409

    if estado == "solapamiento":
        return jsonify({
            "error": (
                "El paciente ya posee un turno activo reservado "
                "con este médico en la misma franja horaria."
            )
        }), 409

    if estado == "error":
        return jsonify({
            "error": "No se pudo completar la reserva por un error interno."
        }), 500

    # 5. Preparar la respuesta.
    turno = resultado["turno"]
    fecha_hora = turno["fecha_hora"]

    if hasattr(fecha_hora, "strftime"):
        fecha_hora = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
    else:
        fecha_hora = str(fecha_hora)

    return jsonify({
        "mensaje": "Turno reservado exitosamente.",
        "reserva": {
            "id_turno": id_turno,
            "id_paciente": id_paciente,
            "fecha_hora": fecha_hora,
            "estado": "reservado",
            "token_qr": codigo_qr_hash
        }
    }), 200