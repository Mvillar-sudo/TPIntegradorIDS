from flask import Blueprint, Response, abort, flash, redirect, render_template, session, url_for

from services import turnos as turnos_service
from services.api_client import SIN_CONEXION
from services.sesion import ir_al_login

turnos_bp = Blueprint('turnos', __name__)


def exigir_paciente():
    """
    Pre: -
    Post: Devuelve None si hay un paciente con sesión iniciada. Si no, devuelve la respuesta
          (una redirección con un mensaje) que la ruta tiene que devolver.
    """
    if 'token' not in session:
        return ir_al_login('Iniciá sesión para continuar')

    if session.get('usuario', {}).get('rol') != 'paciente':
        flash('Esta pantalla es solo para pacientes', 'error')
        return redirect(url_for('public.index'))

    return None


@turnos_bp.route('/mis-turnos', methods=['GET'])
def mis_turnos():
    rechazo = exigir_paciente()
    if rechazo is not None:
        return rechazo

    datos, error, status = turnos_service.listar_mis_turnos()

    if status == 401:
        return ir_al_login('Tu sesión expiró, iniciá sesión nuevamente')

    if error is not None:
        flash(error, 'error')
        return redirect(url_for('public.index'))

    return render_template(
        'turnos/mis_turnos.html', proximos=datos['proximos'], anteriores=datos['anteriores']
    )


@turnos_bp.route('/turnos/<int:id_turno>/qr.png', methods=['GET'])
def imagen_qr(id_turno):
    if 'token' not in session:
        abort(401)

    if session.get('usuario', {}).get('rol') != 'paciente':
        abort(403)

    imagen, error, status = turnos_service.obtener_qr(id_turno)

    if error is not None:
        abort(status if status in (400, 401, 403, 404) else 502)

    return Response(imagen, mimetype='image/png')


@turnos_bp.route('/turnos/<int:id_turno>/cancelar', methods=['GET'])
def confirmar_cancelacion(id_turno):
    rechazo = exigir_paciente()
    if rechazo is not None:
        return rechazo

    turno, error, status = turnos_service.obtener_mi_turno(id_turno)

    if status == 401:
        return ir_al_login('Tu sesión expiró, iniciá sesión nuevamente')

    if status == SIN_CONEXION or (error is not None and status != 404):
        flash(error, 'error')
        return redirect(url_for('public.index'))

    return render_template('turnos/cancelar.html', turno=turno, error=error)


@turnos_bp.route('/turnos/<int:id_turno>/cancelar', methods=['POST'])
def cancelar(id_turno):
    rechazo = exigir_paciente()
    if rechazo is not None:
        return rechazo

    _, error, status = turnos_service.cancelar_turno(id_turno)

    if status == 401:
        return ir_al_login('Tu sesión expiró, iniciá sesión nuevamente')

    if error is not None:
        flash(error, 'error')
        return redirect(url_for('turnos.confirmar_cancelacion', id_turno=id_turno))

    flash('Tu turno fue cancelado. Podés reservar otro cuando quieras.', 'success')
    return redirect(url_for('turnos.mis_turnos'))
