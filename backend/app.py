from flask import Flask, jsonify

from backend.routes.admin import admin_bp
from backend.routes.agendas import agendas_bp
from backend.routes.auth import auth_bp
from backend.routes.medicos import medicos_bp

app = Flask(__name__)
app.json.sort_keys = False
app.register_blueprint(auth_bp, url_prefix='/api/v1')
app.register_blueprint(admin_bp, url_prefix='/api/v1')
app.register_blueprint(medicos_bp, url_prefix='/api/v1')
app.register_blueprint(agendas_bp, url_prefix='/api/v1')


@app.errorhandler(RuntimeError)
def database_unavailable(_error):
	return jsonify({'error': 'Base de datos no disponible'}), 503


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000',debug='true')