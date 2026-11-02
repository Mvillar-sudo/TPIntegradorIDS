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
    
    # Si execute_query devolvió None (error de conexión o de BD)
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