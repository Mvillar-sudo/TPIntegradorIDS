from flask import Blueprint, flash, redirect, render_template, session, url_for
from services.medico import obtener_agenda_medico, registrar_turno_atendido

medico_bp = Blueprint('medico', __name__)


@medico_bp.before_request
def exigir_medico():
    """
    Pre: -
    Post: Redirige si el usuario no tiene sesión iniciada o su rol no es 'medico'.
    """
    if 'token' not in session or 'usuario' not in session:
        flash('Iniciá sesión para continuar', 'danger')
        return redirect(url_for('auth.iniciar_sesion'))

    if session.get('usuario', {}).get('rol') != 'medico':
        flash('Acceso denegado: Se requiere rol de profesional médico.', 'danger')
        return redirect(url_for('index'))

"""
Pre: -
Post: Renderiza la plantilla 'medico.html' con la información del médico y la lista de turnos asignados.
"""
@medico_bp.route('/medico', methods=['GET'])
def agenda():
    try:
        perfil, turnos, turnos_espera = obtener_agenda_medico()
    except ValueError as e:
        flash(str(e), 'danger')
        usuario = session.get('usuario', {})
        nombre = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
        perfil = {
            'nombre': nombre or 'Profesional Médico',
            'consultorio': '-',
            'especialidad': '-',
        }
        turnos = []
        turnos_espera = []

    return render_template('medico.html', medico=perfil, turnos=turnos, turnos_espera=turnos_espera)

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
