from flask import Blueprint, abort, flash, redirect, render_template, session, url_for

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Cada ítem del menú lateral: (texto, endpoint). Agregar un ABM nuevo = una línea acá.
MENU_ADMIN = [
    ('Inicio', 'admin.dashboard'),
    ('Médicos', 'admin.listado_medicos'),
]


@admin_bp.before_request
def exigir_admin():
    """Protege todo /admin: hay que estar logueado y ser admin."""
    if 'token' not in session:
        flash('Iniciá sesión para continuar', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if session.get('usuario', {}).get('rol') != 'admin':
        abort(403)


def redirigir_por_sesion_vencida():
    """Las rutas la usan cuando el backend responde 401 (token vencido)."""
    session.clear()
    flash('Tu sesión expiró, iniciá sesión nuevamente', 'error')
    return redirect(url_for('auth.iniciar_sesion'))


@admin_bp.context_processor
def inyectar_menu():
    return {'menu_admin': MENU_ADMIN}


@admin_bp.route('/')
def dashboard():
    return render_template('admin/dashboard.html')


# Vistas solo visuales (sin conexión al backend todavía)
@admin_bp.route('/medicos')
def listado_medicos():
    return render_template('admin/medicos_listado.html')


@admin_bp.route('/medicos/nuevo')
def nuevo_medico():
    return render_template('admin/medicos_form.html', titulo='Nuevo médico')


@admin_bp.route('/medicos/editar')
def editar_medico():
    return render_template('admin/medicos_form.html', titulo='Editar médico')
