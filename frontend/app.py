import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from routes.recepcion import recepcion_bp

try:
    from services.medico import (
        obtener_perfil_medico,
        obtener_turnos_hoy,
        registrar_turno_atendido,
    )
except ImportError:
    from frontend.services.medico import (
        obtener_perfil_medico,
        obtener_turnos_hoy,
        registrar_turno_atendido,
    )

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FRONTEND_SECRET_KEY', 'clave_secreta_mockup_centro_medico')

medico_bp = Blueprint('medico', __name__)

"""
Pre: -
Post: Renderiza la plantilla 'medico.html' con la información del médico y la lista de turnos asignados.
"""
@medico_bp.route('/medico', methods=['GET'])
def agenda():
    perfil = obtener_perfil_medico()
    turnos = obtener_turnos_hoy()
    return render_template('medico.html', medico=perfil, turnos=turnos)

"""
Pre: 'id_turno' es un entero positivo que identifica al turno a atender.
Post: Registra el turno como atendido y redirige a la agenda limpia evitando reenvío de formularios.
"""
@medico_bp.route('/medico/turnos/<int:id_turno>/atender', methods=['POST'])
def atender_turno(id_turno):
    try:
        resultado = registrar_turno_atendido(id_turno)
        flash(f'Consulta finalizada con éxito. Turno #{id_turno} marcado como atendido.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('medico.agenda'))


app.register_blueprint(medico_bp)
app.register_blueprint(recepcion_bp)


if __name__ == '__main__':
    app.run(port=5001, debug=True)