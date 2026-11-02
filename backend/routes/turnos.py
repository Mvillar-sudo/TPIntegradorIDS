from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from auth_middleware import token_required

turnos_bp = Blueprint('turnos', __name__)


@turnos_bp.route('/api/v1/turnos/mis-turnos', methods=['GET'])
@token_required()
def obtener_mis_turnos():
    usuario = request.user_data
    id_usuario = usuario.get("id_usuario") or usuario.get("id")
    
    return jsonify({
        "status": "success",
        "mensaje": f"Lista de turnos para el usuario {id_usuario}"
    }), 200


@turnos_bp.route('/api/v1/turnos/<int:id_turno>/cancelar', methods=['POST'])
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
