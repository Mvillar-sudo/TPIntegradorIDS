from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services import recepcion as recepcion_service

recepcion_bp = Blueprint('recepcion', __name__, url_prefix='/recepcion')


@recepcion_bp.route('/', methods=['GET'])
def pantalla_recepcion():
    checkin = session.pop('checkin', None)
    sala_espera = recepcion_service.obtener_sala_espera()

    return render_template('recepcion.html', checkin=checkin, sala_espera=sala_espera)


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