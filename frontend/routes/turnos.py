from flask import Blueprint, flash, redirect, render_template, session, url_for

from routes.admin import redirigir_por_sesion_vencida
from services import turnos as turnos_service
from services.api_client import SIN_CONEXION

turnos_bp = Blueprint('turnos', __name__)


def exigir_paciente():
    """
    Pre: -
    Post: Devuelve None si hay un paciente con sesión iniciada. Si no, devuelve la respuesta
          (una redirección con un mensaje) que la ruta tiene que devolver.
    """
    if 'token' not in session:
        flash('Iniciá sesión para cancelar tu turno', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if session.get('usuario', {}).get('rol') != 'paciente':
        flash('Esta pantalla es solo para pacientes', 'error')
        return redirect(url_for('index'))

    return None


@turnos_bp.route('/turnos/<int:id_turno>/cancelar', methods=['GET'])
def confirmar_cancelacion(id_turno):
    rechazo = exigir_paciente()
    if rechazo is not None:
        return rechazo

    turno, error, status = turnos_service.obtener_mi_turno(id_turno)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if status == SIN_CONEXION or (error is not None and status != 404):
        flash(error, 'error')
        return redirect(url_for('index'))

    return render_template('turnos/cancelar.html', turno=turno, error=error)


@turnos_bp.route('/turnos/<int:id_turno>/cancelar', methods=['POST'])
def cancelar(id_turno):
    rechazo = exigir_paciente()
    if rechazo is not None:
        return rechazo

    _, error, status = turnos_service.cancelar_turno(id_turno)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error is not None:
        flash(error, 'error')
    else:
        flash('Tu turno fue cancelado. Podés reservar otro cuando quieras.', 'success')

    return redirect(url_for('turnos.confirmar_cancelacion', id_turno=id_turno))
