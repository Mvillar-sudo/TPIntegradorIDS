from flask import abort, flash, redirect, render_template, session, url_for

# Cada ítem del menú lateral: (texto, endpoint). Agregar un ABM nuevo = una línea acá.
MENU_ADMIN = [
    ('Inicio', 'admin.dashboard'),
    ('Resumen', 'admin.resumen'),
    ('Médicos', 'admin.listado_medicos'),
]


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


def renderizar_admin(plantilla, titulo='', resumen=None):
    """Renderiza una plantilla de admin inyectando el menú lateral."""
    return render_template(plantilla, menu_admin=MENU_ADMIN, titulo=titulo, resumen=resumen)
