import os
from dotenv import load_dotenv
from flask import Flask, render_template

from constants import FRONTEND_SECRET_KEY
from routes.auth import auth_bp
from routes.medico import medico_bp
from routes.recepcion import recepcion_bp
from routes.admin import admin_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = FRONTEND_SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(medico_bp)
app.register_blueprint(recepcion_bp)
app.register_blueprint(admin_bp)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/elements')
def prueba_template():
    return render_template('base_template.html')


if __name__ == "__main__":
    app.run(port=3000, debug=True)
