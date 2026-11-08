from flask import Blueprint, flash
from services.admin import verificar_admin, renderizar_admin, redirigir_por_sesion_vencida
from services.api_client import pedir

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def dashboard():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo
    return renderizar_admin('admin/dashboard.html')


@admin_bp.route('/resumen')
def resumen():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    datos, error, status = pedir('GET', '/admin/resumen')

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')
        datos = {}

    return renderizar_admin('admin/resumen.html', resumen=datos)


# Vistas solo visuales (sin conexión al backend todavía)
@admin_bp.route('/medicos')
def listado_medicos():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo
    return renderizar_admin('admin/medicos_listado.html')


@admin_bp.route('/medicos/nuevo')
def nuevo_medico():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo
    return renderizar_admin('admin/medicos_form.html', titulo='Nuevo médico')


@admin_bp.route('/medicos/editar')
def editar_medico():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo
    return renderizar_admin('admin/medicos_form.html', titulo='Editar médico')
