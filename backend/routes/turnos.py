import uuid
import hashlib
from datetime import datetime
from flask import Blueprint, jsonify, request

try:
    from db import execute_query
    from auth_middleware import token_required
except ImportError:
    from backend.db import execute_query
    from backend.auth_middleware import token_required

turnos_bp = Blueprint('turnos', __name__, url_prefix='/api/v1')

@turnos_bp.route('/especialidades', methods=['GET'])
def obtener_especialidades():
    query = "SELECT id_especialidad, nombre_especialidad FROM especialidades ORDER BY nombre_especialidad ASC;"
    resultados = execute_query(query)
    
    if resultados is None:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500
    
    especialidades = [
        {
            "id_especialidad": row["id_especialidad"],
            "nombre": row["nombre_especialidad"]
        }
        for row in resultados
    ]
    
    return jsonify(especialidades), 200

@turnos_bp.route('/medicos', methods=['GET'])
def obtener_medicos():
    especialidad_id = request.args.get('especialidad_id')
    
    query = """
        SELECT 
            m.id_medico, 
            m.nombre_medico AS nombre, 
            m.apellido_medico AS apellido, 
            m.id_especialidad, 
            e.nombre_especialidad AS especialidad
        FROM medicos m
        INNER JOIN especialidades e ON m.id_especialidad = e.id_especialidad
    """
    params = []
    
    if especialidad_id:
        try:
            params.append(int(especialidad_id))
            query += " WHERE m.id_especialidad = %s"
        except ValueError:
            return jsonify({"error": "El parametro especialidad_id debe ser un numero entero valido"}), 400

    query += " ORDER BY m.apellido_medico ASC, m.nombre_medico ASC;"
    
    resultados = execute_query(query, tuple(params) if params else None)
    
    if resultados is None:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500
    
    medicos = [
        {
            "id_medico": row["id_medico"],
            "nombre": row["nombre"],
            "apellido": row["apellido"],
            "id_especialidad": row["id_especialidad"],
            "especialidad": row["especialidad"]
        }
        for row in resultados
    ]
    
    return jsonify(medicos), 200

@turnos_bp.route('/turnos/disponibles', methods=['GET'])
def obtener_turnos_disponibles():
    medico_id = request.args.get('medico_id')
    fecha = request.args.get('fecha')
    especialidad_id = request.args.get('especialidad_id')

    query = """
        SELECT 
            t.id_turno,
            t.id_medico,
            m.nombre_medico,
            m.apellido_medico,
            e.id_especialidad,
            e.nombre_especialidad,
            t.id_consultorio,
            c.numero_consultorio,
            c.piso,
            t.fecha_hora,
            t.estado
        FROM turnos t
        INNER JOIN medicos m ON t.id_medico = m.id_medico
        INNER JOIN especialidades e ON m.id_especialidad = e.id_especialidad
        INNER JOIN consultorios c ON t.id_consultorio = c.id_consultorio
        WHERE t.estado = 'disponible'
    """
    params = []

    if medico_id:
        try:
            params.append(int(medico_id))
            query += " AND t.id_medico = %s"
        except ValueError:
            return jsonify({"error": "El parametro medico_id debe ser un numero entero valido"}), 400

    if especialidad_id:
        try:
            params.append(int(especialidad_id))
            query += " AND e.id_especialidad = %s"
        except ValueError:
            return jsonify({"error": "El parametro especialidad_id debe ser un numero entero valido"}), 400

    if fecha:
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            params.append(fecha)
            query += " AND DATE(t.fecha_hora) = %s"
        except ValueError:
            return jsonify({"error": "El parametro fecha debe tener el formato YYYY-MM-DD"}), 400

    query += " ORDER BY t.fecha_hora ASC;"

    resultados = execute_query(query, tuple(params) if params else None)

    if resultados is None:
        return jsonify({"error": "No se pudo conectar a la base de datos o fallo la consulta"}), 500

    turnos_disponibles = []
    for row in resultados:
        fecha_hora_str = row["fecha_hora"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row["fecha_hora"], "strftime") else str(row["fecha_hora"])
        turnos_disponibles.append({
            "id_turno": row["id_turno"],
            "id_medico": row["id_medico"],
            "medico": f"{row['nombre_medico']} {row['apellido_medico']}",
            "id_especialidad": row["id_especialidad"],
            "especialidad": row["nombre_especialidad"],
            "id_consultorio": row["id_consultorio"],
            "consultorio": f"Consultorio {row['numero_consultorio']} ({row['piso']})",
            "fecha_hora": fecha_hora_str,
            "estado": row["estado"]
        })

    return jsonify(turnos_disponibles), 200

@turnos_bp.route('/turnos/reservar', methods=['POST'])
@token_required()
def reservar_turno():
    user_data = getattr(request, 'user_data', {})
    id_paciente = user_data.get('id_usuario')

    if not id_paciente:
        return jsonify({"error": "El token no contiene un id_usuario valido"}), 401

    data = request.get_json()
    if not data or 'id_turno' not in data:
        return jsonify({"error": "Debe proporcionar el id_turno en el cuerpo de la peticion"}), 400

    try:
        id_turno = int(data['id_turno'])
    except ValueError:
        return jsonify({"error": "El id_turno debe ser un numero entero valido"}), 400

    # 1. Verificar existencia y estado del turno
    query_turno = """
        SELECT id_turno, id_medico, fecha_hora, estado 
        FROM turnos 
        WHERE id_turno = %s;
    """
    res_turno = execute_query(query_turno, (id_turno,))

    if res_turno is None:
        return jsonify({"error": "Error al consultar la base de datos"}), 500

    if not res_turno:
        return jsonify({"error": "El turno solicitado no existe"}), 404

    turno = res_turno[0]

    if turno['estado'] != 'disponible':
        return jsonify({"error": "El turno ya no se encuentra disponible"}), 409

    # 2. Validar restriccion de solapamiento (mismo paciente y mismo medico en la misma fecha/hora)
    query_solapamiento = """
        SELECT id_turno 
        FROM turnos 
        WHERE id_paciente = %s 
          AND id_medico = %s 
          AND fecha_hora = %s 
          AND estado IN ('reservado', 'confirmado');
    """
    res_solapamiento = execute_query(query_solapamiento, (id_paciente, turno['id_medico'], turno['fecha_hora']))

    if res_solapamiento is None:
        return jsonify({"error": "Error al validar restricciones de la reserva"}), 500

    if len(res_solapamiento) > 0:
        return jsonify({
            "error": "El paciente ya posee un turno activo reservado con este medico en la misma franja horaria"
        }), 409

    # 3. Generar token hash unico para el codigo QR
    semilla = f"TURNO-{id_turno}-PACIENTE-{id_paciente}-{datetime.now().isoformat()}-{uuid.uuid4().hex}"
    codigo_qr_hash = hashlib.sha256(semilla.encode('utf-8')).hexdigest()

    # 4. Asignar el turno al paciente y marcarlo como reservado
    query_update = """
        UPDATE turnos 
        SET id_paciente = %s, 
            estado = 'reservado', 
            token_qr = %s 
        WHERE id_turno = %s AND estado = 'disponible';
    """
    filas_afectadas = execute_query(query_update, (id_paciente, codigo_qr_hash, id_turno))

    if filas_afectadas is None or filas_afectadas == 0:
        return jsonify({"error": "No se pudo concretar la reserva. El turno pudo haber sido tomado recientemente"}), 409

    fecha_hora_str = turno['fecha_hora'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(turno['fecha_hora'], "strftime") else str(turno['fecha_hora'])

    return jsonify({
        "mensaje": "Turno reservado exitosamente",
        "reserva": {
            "id_turno": id_turno,
            "id_paciente": id_paciente,
            "fecha_hora": fecha_hora_str,
            "estado": "reservado",
            "token_qr": codigo_qr_hash
        }
    }), 200