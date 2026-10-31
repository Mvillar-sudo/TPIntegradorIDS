from flask import Flask, jsonify

try:
    from routes.checkin_qr import checkin_qr_bp
    from routes.medico import medico_bp
except ImportError:
    from backend.routes.checkin_qr import checkin_qr_bp
    from backend.routes.medico import medico_bp

app = Flask(__name__)

# Para las tildes y caracteres especiales en JSON
app.json.ensure_ascii = False

app.register_blueprint(checkin_qr_bp)
app.register_blueprint(medico_bp)


@app.route("/")
def home():
    return jsonify({"mensaje": "API Centro Médico Salud Integral activa"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "La ruta solicitada no existe"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método HTTP no permitido para esta ruta"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno en el servidor"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
