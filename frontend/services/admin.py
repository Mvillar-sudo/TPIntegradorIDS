from datetime import datetime

from flask import abort, flash, redirect, render_template, session, url_for

from services.api_client import pedir

# Cada ítem del menú lateral: (texto, endpoint). Agregar un ABM nuevo = una línea acá.
MENU_ADMIN = [
    ('Inicio', 'admin.dashboard'),
    ('Médicos', 'admin.listado_medicos'),
    ('Agendas', 'admin.menu_agendas'),
]

FORMATO_FECHA_HORA = '%d/%m/%Y %H:%M'


def verificar_admin():
    """Protege las rutas de /admin: hay que estar logueado y ser admin.

    Devuelve None si todo está bien, o una redirección si falta iniciar sesión.
    Si el usuario no es admin corta con 403.
    """
    if 'token' not in session:
        flash('Iniciá sesión para continuar', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if session.get('usuario', {}).get('rol') != 'admin':
        abort(403)

    return None


def redirigir_por_sesion_vencida():
    """Las rutas la usan cuando el backend responde 401 (token vencido)."""
    session.clear()
    flash('Tu sesión expiró, iniciá sesión nuevamente', 'error')
    return redirect(url_for('auth.iniciar_sesion'))


def obtener_estadisticas():
    """Pide al backend los totales del panel (médicos, especialidades, turnos de hoy y pacientes).

    Devuelve (datos, error, status). Si hay error, datos queda como {} para que la
    plantilla muestre "-" en cada tarjeta.
    """
    datos, error, status = pedir('GET', '/admin/resumen')
    return (datos if not error else {}), error, status


def obtener_medicos_admin():
    """Pide al backend el listado de médicos.

    Devuelve (datos, error, status). Si hay error, datos queda como [] para que la
    plantilla muestre la tabla vacía.
    """
    datos, error, status = pedir('GET', '/medicos')
    return (datos if not error else []), error, status


def obtener_especialidades_admin():
    """Pide al backend las especialidades para el formulario de médicos.

    Devuelve (datos, error, status). Si hay error, datos queda como [] para que el
    desplegable aparezca vacío.
    """
    datos, error, status = pedir('GET', '/especialidades')
    return (datos if not error else []), error, status


def crear_medico_admin(form):
    """Da de alta un médico: primero crea el usuario con rol médico y después su perfil.

    Devuelve (datos, error, status). Antes de crear nada se valida lo que haría fallar al perfil
    (especialidad y matrícula única), para no dejar un usuario médico sin perfil.
    Si falla la creación del usuario no se intenta el perfil.
    """
    matricula = form.get('matricula', '').strip()

    if form.get('id_especialidad', type=int) is None:
        return None, 'Elegí una especialidad', 400

    if not matricula:
        return None, 'La matrícula es obligatoria', 400

    if len(matricula) > 50:
        return None, 'La matrícula no puede superar los 50 caracteres', 400

    disponibilidad, error, status = pedir('GET', '/medicos/matricula-disponible', params={'matricula': matricula})
    if error:
        return None, error, status

    if not disponibilidad['disponible']:
        return None, 'La matrícula ingresada ya existe', 409

    usuario, error, status = pedir('POST', '/usuarios', json={
        'rol': 'medico',
        'nombre': form.get('nombre', '').strip(),
        'apellido': form.get('apellido', '').strip(),
        'dni': form.get('dni', '').strip(),
        'email': form.get('email', '').strip(),
        'telefono': form.get('telefono', '').strip(),
        'password': form.get('password', ''),
    })
    if error:
        return None, error, status

    return pedir('POST', '/medicos', json={
        'id_usuario': usuario['usuario']['id_usuario'],
        'id_especialidad': form.get('id_especialidad', type=int),
        'matricula': matricula,
    })


def obtener_medico_admin(id_medico):
    """Pide al backend los datos de un médico. Devuelve (datos, error, status)."""
    return pedir('GET', f'/medicos/{id_medico}')


def actualizar_medico_admin(id_medico, form):
    """Envía al backend los datos editados de un médico. Devuelve (datos, error, status)."""
    return pedir('PATCH', f'/medicos/{id_medico}', json={
        'nombre': form.get('nombre', '').strip(),
        'apellido': form.get('apellido', '').strip(),
        'dni': form.get('dni', '').strip(),
        'email': form.get('email', '').strip(),
        'telefono': form.get('telefono', '').strip(),
        'matricula': form.get('matricula', '').strip(),
        'id_especialidad': form.get('id_especialidad', type=int),
    })


def eliminar_medico_admin(id_medico):
    """Pide al backend eliminar un médico. Devuelve (datos, error, status); sin error el backend responde 204."""
    return pedir('DELETE', f'/medicos/{id_medico}')


def datos_form_medico(medico):
    """Convierte un médico del backend en los valores que precargan el formulario."""
    return {
        'nombre': medico.get('nombre_medico') or '',
        'apellido': medico.get('apellido_medico') or '',
        'dni': medico.get('dni_medico') or '',
        'email': medico.get('email_medico') or '',
        'telefono': medico.get('telefono_medico') or '',
        'matricula': medico.get('matricula') or '',
        'id_especialidad': str(medico.get('id_especialidad') or ''),
    }


def formatear_fecha_hora(valor):
    """Convierte una fecha ISO del backend (2026-12-01T09:00:00) en 01/12/2026 09:00."""
    try:
        return datetime.fromisoformat(valor).strftime(FORMATO_FECHA_HORA)
    except (TypeError, ValueError):
        return valor or '-'


def formatear_agenda(agenda):
    """Convierte una agenda del backend en los textos que muestra la tabla."""
    consultorio = f"Consultorio {agenda.get('numero_consultorio', '-')}"
    if agenda.get('piso'):
        consultorio += f" ({agenda['piso']})"

    return {
        'id': agenda.get('id_agenda'),
        'medico': f"{agenda.get('apellido_medico', '')}, {agenda.get('nombre_medico', '')}",
        'consultorio': consultorio,
        'inicio': formatear_fecha_hora(agenda.get('agenda_fecha_hora_inicio')),
        'fin': formatear_fecha_hora(agenda.get('agenda_fecha_hora_fin')),
    }


def obtener_agendas_admin():
    """Pide al backend todas las agendas creadas.

    Devuelve (datos, error, status). Si hay error, datos queda como [] para que la
    plantilla muestre la tabla vacía.
    """
    datos, error, status = pedir('GET', '/agendas')
    if error:
        return [], error, status
    return [formatear_agenda(agenda) for agenda in datos], None, status


def eliminar_agenda_admin(id_agenda):
    """Pide al backend eliminar una agenda. Devuelve (datos, error, status); sin error el backend responde 204."""
    return pedir('DELETE', f'/agendas/{id_agenda}')


def renderizar_admin(plantilla, titulo='', estadisticas=None, medicos=None,
                     especialidades=None, form=None, edicion=False, agendas=None):
    """Renderiza una plantilla de admin inyectando el menú lateral."""
    return render_template(
        plantilla, menu_admin=MENU_ADMIN, titulo=titulo,
        estadisticas=estadisticas, medicos=medicos,
        especialidades=especialidades, form=form or {}, edicion=edicion,
        agendas=agendas
    )
