import requests
import os 
from constants import BACKEND_URL
from flask import (request, Blueprint, render_template, flash, redirect, url_for, session)



auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def mostrar_registro():
    if request.method == 'GET':
        return render_template('register.html')

    if request.form['password'] != request.form['password_confirm']:
        flash('Las contraseñas no coinciden', 'error')
        return render_template('register.html')

    payload = {
        "nombre": request.form['nombre'],
        "apellido": request.form['apellido'],
        "dni": request.form['dni'],
        "email": request.form['email'],
        "password": request.form['password'],
        "telefono": request.form.get('telefono') or None,
    }

    try:
        r = requests.post(f"{BACKEND_URL}/auth/register", json=payload, timeout=5)
        datos = r.json()
    except requests.exceptions.RequestException:
        flash('No se pudo conectar con el servidor', 'error')
        return render_template('register.html')

    if r.status_code == 201:
        flash(datos['mensaje'], 'success')
        return redirect(url_for('public.index'))   # o a /login cuando exista

    flash(datos.get('error', 'Error al registrar'), 'error')
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'GET':
        return render_template('login.html')

    payload = {
        "email": request.form['email'],
        "password": request.form['password'],
    }

    try:
        r = requests.post(f"{BACKEND_URL}/auth/login", json=payload, timeout=5)
        datos = r.json()
    except (requests.exceptions.RequestException, ValueError):
        flash('No se pudo conectar con el servidor', 'error')
        return render_template('login.html')

    if r.status_code == 200:
        session['token'] = datos['token']
        session['usuario'] = datos['usuario']
        flash(datos['mensaje'], 'success')
        return redirect(url_for('public.index'))

    flash(datos.get('error', 'Error al iniciar sesión'), 'error')
    return render_template('login.html')


@auth_bp.route('/logout')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('public.index'))
