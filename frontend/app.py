from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

from datetime import timedelta
from constants import FRONTEND_SECRET_KEY

from routes.recepcion import recepcion_bp
from routes.auth import auth_bp
from routes.medico import medico_bp
from routes.admin import admin_bp
from routes.public import public_bp
from routes.turnos import turnos_bp
from routes.reservar_turno import reservar_turno_bp
from routes.errores import errores_bp


from constants import FRONTEND_SECRET_KEY

from services.agendas import obtener_medicos, crear_agenda
from services.medico import (obtener_perfil_medico, obtener_turnos_hoy, registrar_turno_atendido)

app = Flask(__name__)
app.secret_key = FRONTEND_SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=2)

app.register_blueprint(auth_bp)
app.register_blueprint(medico_bp)
app.register_blueprint(recepcion_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(public_bp)
app.register_blueprint(turnos_bp)
app.register_blueprint(reservar_turno_bp)
app.register_blueprint(errores_bp)



if __name__ == "__main__":
    app.run(port=3000, debug=False)
