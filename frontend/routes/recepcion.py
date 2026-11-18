from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services import recepcion as recepcion_service
from services.agendas import obtener_medicos, obtener_consultorios, crear_agenda_desde_formulario
from services.sesion import exigir_rol

# 1. Definimos el Blueprint UNA sola vez con su prefijo
recepcion_bp = Blueprint('recepcion', __name__, url_prefix='/recepcion')


"""
Pre: -
Post: Redirige al login si no hay sesión iniciada, o muestra el acceso denegado (403) si el usuario
      no tiene rol de recepcionista o admin.
"""
@recepcion_bp.before_request
def exigir_recepcionista():
    return exigir_rol(('recepcionista', 'admin'))


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

@recepcion_bp.route('/agenda/configurar', methods=['GET'])
def configurar_agenda():
    """
    Pre: -
    Post: Obtiene los médicos y consultorios de la API y renderiza el formulario. Si la API falla,
          muestra el mensaje de error y el formulario vacío.
    """
    usuario_actual = session.get('usuario')

    try:
        lista_medicos = obtener_medicos()
        lista_consultorios = obtener_consultorios()
        return render_template('configurar_agenda.html', medicos=lista_medicos,
                               consultorios=lista_consultorios, usuario=usuario_actual)
    except ValueError as error:
        flash(str(error), 'danger')
        return render_template('configurar_agenda.html', medicos=[], consultorios=[], usuario=usuario_actual)


@recepcion_bp.route('/agenda/guardar', methods=['POST'])
def guardar_agenda():
    """
    Pre: el formulario trae medico_id, consultorio_id, duracion_turno, fecha_inicio, hora_inicio,
         fecha_fin y hora_fin.
    Post: Crea la agenda en el backend y vuelve al formulario con un mensaje de éxito o con el
          motivo por el que no se pudo.
    """
    try:
        crear_agenda_desde_formulario(request.form)
    except ValueError as error:
        flash(f'Error al crear la agenda: {error}', 'danger')
        return redirect(url_for('recepcion.configurar_agenda'))

    flash('La agenda se generó correctamente.', 'success')
    return redirect(url_for('recepcion.configurar_agenda'))
