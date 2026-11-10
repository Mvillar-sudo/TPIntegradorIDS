from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services import recepcion as recepcion_service

recepcion_bp = Blueprint('recepcion', __name__, url_prefix='/recepcion')


"""
Pre: -
Post: Redirige al login si no hay sesión iniciada, o a la home si el usuario no tiene rol de recepcionista o admin.
"""
@recepcion_bp.before_request
def exigir_recepcionista():
    if 'token' not in session or 'usuario' not in session:
        flash('Iniciá sesión para continuar', 'danger')
        return redirect(url_for('auth.iniciar_sesion'))

    rol = session.get('usuario', {}).get('rol')
    if rol not in ('recepcionista', 'admin'):
        flash('Acceso denegado: Se requiere rol de recepción o administración.', 'danger')
        return redirect(url_for('index'))


"""
Pre: -
Post: Renderiza la plantilla 'recepcion.html' con los datos del check-in procesado y la sala de espera.
"""
@recepcion_bp.route('/', methods=['GET'])
def pantalla_recepcion():
    checkin = session.pop('checkin', None)
    sala_espera = recepcion_service.obtener_sala_espera()

    return render_template('recepcion.html', checkin=checkin, sala_espera=sala_espera)


"""
Pre: 'token_qr' debe ser una cadena no vacía enviada en el formulario.
Post: Procesa el check-in del paciente llamando a la API y guarda el resultado en sesión.
"""
@recepcion_bp.route('/checkin', methods=['POST'])
def registrar_checkin():
    token_qr = request.form.get('token_qr', '').strip()

    if not token_qr:
        flash('Ingresá o escaneá un código QR.', 'error')
        return redirect(url_for('recepcion.pantalla_recepcion'))

    try:
        session['checkin'] = recepcion_service.registrar_checkin(token_qr)
    except ValueError as error:
        flash(str(error), 'error')

    return redirect(url_for('recepcion.pantalla_recepcion'))
