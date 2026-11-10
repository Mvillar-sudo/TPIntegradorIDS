import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session, Blueprint
from routes.recepcion import recepcion_bp
from services.agendas import obtener_medicos, crear_agenda
from services.medico import (obtener_perfil_medico, obtener_turnos_hoy, registrar_turno_atendido)
    
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

# --- ISSUE 3: RUTAS DEL ADMINISTRADOR / MÉDICO (Agendas) ---
"""
Pre: -
Post: Renderiza el formulario para crear agendas (GET) o captura los datos del form y los envía al backend (POST).
"""
@app.route('/admin/agendas/nueva', methods=['GET', 'POST'])
def nueva_agenda():
    # Simulamos el usuario actual en sesión (puedes ajustarlo cuando implementes login real)
    usuario_actual = session.get('usuario', {'rol': 'admin'}) 

    if request.method == 'GET':
        try:
            lista_medicos = obtener_medicos()
            return render_template('configurar_agenda.html', medicos=lista_medicos, usuario=usuario_actual)
        except Exception as e:
            flash('Error al conectar con el backend para traer médicos.', 'danger')
            return render_template('configurar_agenda.html', medicos=[], usuario=usuario_actual)

    if request.method == 'POST':
        # Capturamos los datos enviados desde configurar_agenda.html
        datos_formulario = {
            'medico_id': request.form.get('medico_id'),
            'fecha_inicio': request.form.get('fecha_inicio'),
            'fecha_fin': request.form.get('fecha_fin'),
            'hora_inicio': request.form.get('hora_inicio'),
            'hora_fin': request.form.get('hora_fin'),
            'duracion_turno': request.form.get('duracion_turno', 60),
            'dias_atencion': request.form.getlist('dias_atencion')
        }

        # Pasamos los datos al servicio que se comunica con el backend mediante requests
        exito = crear_agenda(datos_formulario)

        if exito:
            flash('La agenda se generó correctamente.', 'success')
        else:
            flash('Hubo un error al generar la agenda en el backend.', 'danger')
            
        return redirect(url_for('nueva_agenda'))

if __name__ == "__main__":
    app.run(port=3000, debug=False)