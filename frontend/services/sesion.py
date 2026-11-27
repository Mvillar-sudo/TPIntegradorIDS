from flask import flash, redirect, request, session, url_for


def ir_al_login(mensaje):
    """
    Pre: 'mensaje' es el texto que se le muestra al usuario.
    Post: Limpia la sesión, guarda la página que estaba pidiendo (para volver ahí después de
          iniciar sesión) y devuelve la redirección al login.
    """
    pagina = request.path
    session.clear()
    session['proxima_pagina'] = pagina
    flash(mensaje, 'error')
    return redirect(url_for('auth.iniciar_sesion'))
