from flask import Flask
from routes.turnos import turnos_bp  # Importación desde la carpeta local routes

app = Flask(__name__)

app.json.ensure_ascii = False

# Registro del Blueprint
app.register_blueprint(turnos_bp)

# Ruta base de prueba
@app.route('/')
def home():
    return {"mensaje": "API Centro Médico Salud Integral activa"}, 200

# Clave para mantener el servidor escuchando en el puerto 5000
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)