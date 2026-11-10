import os
import requests
from flask import (request, Blueprint, render_template, flash, redirect, url_for, session)

from constants import BACKEND_URL, RUTA_POR_ROL

auth_bp = Blueprint("auth", __name__)


"""
Pre: -
Post: Si la petición es GET, renderiza el formulario de registro. Si es POST, valida los datos,
      registra al paciente en el backend y redirige al login ante el éxito, o muestra el error.
"""
@auth_bp.route('/register', methods=['GET', 'POST'])
def mostrar_registro():
    if request.method == 'GET':
        return render_template('register.html', form={})

    form = request.form
    if form.get('password') != form.get('password_confirm'):
        flash('Las contraseñas no coinciden', 'error')
        return render_template('register.html', form=form)

    payload = {
        "nombre": form.get('nombre', '').strip(),
        "apellido": form.get('apellido', '').strip(),
        "dni": form.get('dni', '').strip(),
        "email": form.get('email', '').strip(),
        "password": form.get('password', ''),
        "telefono": form.get('telefono', '').strip() or None,
    }

    try:
        r = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=5)
    except requests.exceptions.RequestException:
        flash('No se pudo conectar con el servidor', 'error')
        return render_template('register.html', form=form)

    try:
        datos = r.json()
    except ValueError:
        datos = {}

    if r.status_code == 201:
        flash('Cuenta creada. Ya podés iniciar sesión', 'success')
        return redirect(url_for('auth.iniciar_sesion'))

    flash(datos.get('error', 'No se pudo registrar el usuario'), 'error')
    return render_template('register.html', form=form)


"""
Pre: -
Post: Si la petición es GET, renderiza el formulario de inicio de sesión. Si es POST, valida
      las credenciales contra el backend, guarda el token y usuario en sesión, emite una
      notificación de bienvenida y redirige a la página de inicio.
"""
@auth_bp.route('/login', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'GET':
        return render_template('login.html')

    payload = {
        "email": request.form.get('email', '').strip(),
        "password": request.form.get('password', ''),
    }

    try:
        r = requests.post(f"{BACKEND_URL}/auth/login", json=payload, timeout=5)
    except requests.exceptions.RequestException:
        flash('No se pudo conectar con el servidor', 'error')
        return render_template('login.html')

    try:
        datos = r.json()
    except ValueError:
        datos = {}

    if r.status_code != 200:
        flash(datos.get('error', 'Error al iniciar sesión'), 'error')
        return render_template('login.html')

    session.clear()
    session.permanent = True
    session['token'] = datos['token']
    session['usuario'] = datos['usuario']

    destino = RUTA_POR_ROL.get(datos['usuario']['rol'], 'public.index')
    return redirect(url_for(destino))


"""
Pre: -
Post: Limpia la sesión actual del usuario y redirige a la página principal.
"""
@auth_bp.route('/logout')
def cerrar_sesion():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('public.index'))
