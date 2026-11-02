from datetime import datetime
from flask import Blueprint, jsonify, request
try:
    from db import execute_query
except ImportError:
    from backend.db import execute_query

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