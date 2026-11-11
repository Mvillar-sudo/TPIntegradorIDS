from flask import Blueprint, flash, redirect, url_for, render_template
from services.medico import (obtener_perfil_medico, obtener_turnos_hoy, registrar_turno_atendido)

medico_bp = Blueprint('medico', __name__)

"""
Pre: -
Post: Renderiza la plantilla 'medico.html' con la información del médico y la lista de turnos asignados desde la API.
"""
@medico_bp.route('/medico', methods=['GET'])
def agenda():
    perfil = obtener_perfil_medico()
    turnos, error, status = obtener_turnos_hoy()
    
    if error:
        flash(error, 'danger')
        
    return render_template('medico.html', medico=perfil, turnos=turnos)

"""
Pre: 'id_turno' es un entero positivo que identifica al turno a atender.
Post: Registra el turno como atendido en el backend y redirige a la agenda.
"""
@medico_bp.route('/medico/turnos/<int:id_turno>/atender', methods=['POST'])
def atender_turno(id_turno):
    datos, error, status = registrar_turno_atendido(id_turno)
    
    if error:
        flash(error, 'danger')
    else:
        flash(f'Consulta finalizada con éxito. Turno #{id_turno} marcado como atendido.', 'success')
        
    return redirect(url_for('medico.agenda'))
