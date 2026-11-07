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

from services.agendas import obtener_medicos, crear_agenda 

recepcion_bp = Blueprint('recepcion', __name__)

@recepcion_bp.route('/recepcion/agenda/configurar', methods=['GET'])
def configurar_agenda():
    """
    Pre: -
    Post: Obtiene los médicos de la API y renderiza el formulario.
    """
    try:
        # Llamamos al servicio para buscar los médicos a la API (puerto 5000)
        lista_medicos = obtener_medicos()
        return render_template('configurar_agenda.html', medicos=lista_medicos)
    except Exception as e:
        flash(f'Error al conectar con la API: {str(e)}', 'danger')
        return render_template('configurar_agenda.html', medicos=[])

@recepcion_bp.route('/recepcion/agenda/guardar', methods=['POST'])
def guardar_agenda():
    try:
        # 1. Capturamos los datos separados del HTML
        f_inicio = request.form.get("fecha_inicio")
        h_inicio = request.form.get("hora_inicio")
        f_fin = request.form.get("fecha_fin")
        h_fin = request.form.get("hora_fin")
        
        # 2. Armamos el diccionario EXACTO que valida tu backend
        datos_backend = {
            "id_medico": int(request.form.get("medico_id")),
            "id_consultorio": 1,  # Fijo por ahora, o sacalo de un select en el HTML
            "agenda_fecha_hora_inicio": f"{f_inicio} {h_inicio}:00",
            "agenda_fecha_hora_fin": f"{f_fin} {h_fin}:00",
            "duracion_turno_minutos": int(request.form.get("duracion_turno"))
        }

        # 3. Llamamos al servicio que hace el POST al backend
        crear_agenda(datos_backend)
        
        flash('La agenda se generó correctamente.', 'success')
        return redirect(url_for('recepcion.configurar_agenda'))
        
    except Exception as e:
        flash(f'Error al crear la agenda: {str(e)}', 'danger')
        return redirect(url_for('recepcion.configurar_agenda'))