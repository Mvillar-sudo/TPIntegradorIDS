from flask import abort, flash, redirect, request, session, url_for


def ir_al_login(mensaje):
    """
    Pre: 'mensaje' es el texto que se le muestra al usuario.
    Post: Limpia la sesión, guarda la página que estaba pidiendo (para volver ahí después de
          iniciar sesión) y devuelve la redirección al login. Solo guarda la página si era un
          GET: a un formulario (POST) no se puede volver entrando por la barra de direcciones.
    """
    pagina = request.path if request.method == 'GET' else None
    session.clear()
    if pagina is not None:
        session['proxima_pagina'] = pagina
    flash(mensaje, 'error')
    return redirect(url_for('auth.iniciar_sesion'))


def exigir_rol(roles):
    """
    Pre: 'roles' es una tupla con los roles que pueden entrar (por ejemplo ('admin',)).
    Post: Devuelve None si hay una sesión iniciada con uno de esos roles. Si no hay sesión,
          devuelve la redirección al login. Si hay sesión pero con otro rol, corta con 403 (la
          página de acceso denegado). Así todas las pantallas responden igual.
    """
    if 'token' not in session or 'usuario' not in session:
        return ir_al_login('Iniciá sesión para continuar')

    if session['usuario'].get('rol') not in roles:
        abort(403)

    return None


def exigir_paciente():
    """
    Pre: -
    Post: Igual que exigir_rol(), pero para las pantallas que son solo de pacientes.
    """
    return exigir_rol(('paciente',))
