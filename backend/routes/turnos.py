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