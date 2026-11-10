from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from services import recepcion as recepcion_service
from services.agendas import obtener_medicos, crear_agenda 

# 1. Definimos el Blueprint UNA sola vez con su prefijo
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

# 2. Arreglamos la ruta (el prefijo ya aporta el /recepcion)
@recepcion_bp.route('/agenda/configurar', methods=['GET'])
def configurar_agenda():
    """
    Pre: -
    Post: Obtiene los médicos de la API y renderiza el formulario.
    """
    # 3. Simulamos el usuario para que Jinja2 no tire error de "undefined"
    usuario_actual = session.get('usuario', {'rol': 'admin'})
    
    try:
        lista_medicos = obtener_medicos()
        # 4. Le pasamos usuario=usuario_actual al template
        return render_template('configurar_agenda.html', medicos=lista_medicos, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al conectar con la API: {str(e)}', 'danger')
        return render_template('configurar_agenda.html', medicos=[], usuario=usuario_actual)

@recepcion_bp.route('/agenda/guardar', methods=['POST'])
def guardar_agenda():
    print("DATOS RECIBIDOS DEL HTML:", request.form)
    try:
        # Capturamos los datos
        medico_id = request.form.get("medico_id")
        duracion_turno = request.form.get("duracion_turno")
        f_inicio = request.form.get("fecha_inicio")
        h_inicio = request.form.get("hora_inicio")
        f_fin = request.form.get("fecha_fin")
        h_fin = request.form.get("hora_fin")

        # Validación: Si falta el médico o la duración (llegan vacíos), avisamos y cortamos
        if not medico_id or not duracion_turno:
            flash('Por favor, seleccioná un médico y especificá la duración del turno.', 'danger')
            return redirect(url_for('recepcion.configurar_agenda'))
        
        datos_backend = {
            "id_medico": int(medico_id),
            "id_consultorio": 1,
            "agenda_fecha_hora_inicio": f"{f_inicio} {h_inicio}:00",
            "agenda_fecha_hora_fin": f"{f_fin} {h_fin}:00",
            "duracion_turno_minutos": int(duracion_turno)
        }

        crear_agenda(datos_backend)
        
        flash('La agenda se generó correctamente.', 'success')
        return redirect(url_for('recepcion.configurar_agenda'))
        
    except Exception as e:
        flash(f'Error al crear la agenda: {str(e)}', 'danger')
        return redirect(url_for('recepcion.configurar_agenda'))
