from flask import Flask, jsonify
from routes.admin import admin_bp
from routes.agendas import agendas_bp
from routes.turnos import turnos_bp  # Importación desde la carpeta local routes
from routes.especialidades import especialidades_bp
from routes.checkin_qr import checkin_qr_bp
from routes.medico import medico_bp
from routes.medicos import medicos_bp
from routes.auth import auth_bp
from routes.usuarios import usuarios_bp
from routes.estadisticas import estadisticas_bp


app = Flask(__name__)

# Para las tildes y caracteres especiales en JSON
app.json.ensure_ascii = False
app.json.sort_keys = False
# Registro del Blueprint
app.register_blueprint(turnos_bp, url_prefix='/api/v1')
app.register_blueprint(especialidades_bp, url_prefix='/api/v1')
app.register_blueprint(admin_bp, url_prefix='/api/v1')
app.register_blueprint(agendas_bp, url_prefix='/api/v1')
app.register_blueprint(checkin_qr_bp, url_prefix='/api/v1')
app.register_blueprint(medico_bp, url_prefix='/api/v1')
app.register_blueprint(medicos_bp, url_prefix="/api/v1")
app.register_blueprint(auth_bp, url_prefix="/api/v1")
app.register_blueprint(usuarios_bp, url_prefix="/api/v1")
app.register_blueprint(estadisticas_bp, url_prefix='/api/v1')


# Ruta base de prueba
@app.route("/")
def home():
    return jsonify({"mensaje": "API Centro Médico Salud Integral activa"}), 200

@app.errorhandler(RuntimeError)
def database_unavailable(_error):
	return jsonify({'error': 'Base de datos no disponible'}), 503

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "La ruta solicitada no existe"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método HTTP no permitido para esta ruta"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno en el servidor"}), 500

  
# Clave para mantener el servidor escuchando en el puerto 5000
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
