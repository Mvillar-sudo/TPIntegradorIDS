import requests
from flask import (request, Blueprint, render_template, flash, redirect, url_for, session)

from constants import BACKEND_URL, RUTA_POR_ROL

auth_bp = Blueprint("auth", __name__)


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


@auth_bp.route('/login', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'GET':
        return render_template('login.html')

    payload = {
        "email": request.form.get('email', ''),
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


@auth_bp.route('/logout')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('public.index'))
