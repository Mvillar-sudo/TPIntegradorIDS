from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from services.agendas import crear_agendas_por_dia, obtener_medicos, obtener_consultorios
from services.admin import verificar_admin, renderizar_admin, redirigir_por_sesion_vencida, obtener_estadisticas, obtener_agendas_admin, eliminar_agenda_admin, obtener_medicos_admin, obtener_especialidades_admin, crear_medico_admin, obtener_medico_admin, actualizar_medico_admin, eliminar_medico_admin, datos_form_medico
from services.api_client import pedir

# Creamos el Blueprint para las rutas de admin del frontend
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/agendas/nueva', methods=['GET', 'POST'])
def nueva_agenda():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    # --- MÉTODO GET: Mostrar el formulario ---
    usuario_actual = session.get('usuario') 

    if request.method == 'GET':
        try:
            lista_medicos = obtener_medicos()
            lista_consultorios = obtener_consultorios()
            return render_template(
                'configurar_agenda.html', 
                medicos=lista_medicos,
                consultorios=lista_consultorios,
                usuario=usuario_actual # Pasamos el usuario al HTML
            )
        except Exception as e:
            flash('Error al cargar datos', 'danger')
            return render_template('configurar_agenda.html', medicos=[], consultorios=[], usuario=usuario_actual)

    # --- MÉTODO POST: Capturar datos y enviar al backend ---
    if request.method == 'POST':
        try:
            creadas, errores = crear_agendas_por_dia(request.form)

            if creadas:
                flash(f'Se crearon {creadas} agenda(s) correctamente.', 'success')
            if errores:
                flash('No se pudieron crear: ' + '; '.join(errores), 'danger')
            return redirect(url_for('admin.nueva_agenda'))

        except Exception as e:
            flash(f'Error al crear la agenda: {str(e)}', 'danger')
            return redirect(url_for('admin.nueva_agenda'))

@admin_bp.route('/')
def dashboard():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    datos, error, status = obtener_estadisticas()

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')

    return renderizar_admin('admin/dashboard.html', estadisticas=datos)


@admin_bp.route('/agendas')
def menu_agendas():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo
    return renderizar_admin('admin/agendas.html')


@admin_bp.route('/agendas/listado')
def listado_agendas():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    datos, error, status = obtener_agendas_admin()

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')

    return renderizar_admin('admin/agendas_listado.html', agendas=datos)


@admin_bp.route('/agendas/<int:id_agenda>/eliminar', methods=['POST'])
def eliminar_agenda(id_agenda):
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    _, error, status = eliminar_agenda_admin(id_agenda)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')
    else:
        flash('Agenda eliminada correctamente', 'success')

    return redirect(url_for('admin.listado_agendas'))


@admin_bp.route('/medicos')
def listado_medicos():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    datos, error, status = obtener_medicos_admin()

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')

    return renderizar_admin('admin/medicos_listado.html', medicos=datos)


@admin_bp.route('/medicos/nuevo', methods=['GET', 'POST'])
def nuevo_medico():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    especialidades, error, status = obtener_especialidades_admin()

    if status == 401:
        return redirigir_por_sesion_vencida()

    if request.method == 'GET':
        if error:
            flash(error, 'error')
        return renderizar_admin('admin/medicos_form.html', titulo='Nuevo médico', especialidades=especialidades)

    # POST: el form vuelve a mostrarse con lo ingresado (sin contraseñas) si algo falla
    form = request.form.to_dict()
    form.pop('password', None)
    form.pop('password_confirm', None)

    if request.form.get('password') != request.form.get('password_confirm'):
        flash('Las contraseñas no coinciden', 'error')
        return renderizar_admin('admin/medicos_form.html', titulo='Nuevo médico', especialidades=especialidades, form=form)

    _, error, status = crear_medico_admin(request.form)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')
        return renderizar_admin('admin/medicos_form.html', titulo='Nuevo médico', especialidades=especialidades, form=form)

    flash('Médico registrado correctamente', 'success')
    return redirect(url_for('admin.listado_medicos'))


@admin_bp.route('/medicos/<int:id_medico>/editar', methods=['GET', 'POST'])
def editar_medico(id_medico):
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    especialidades, error, status = obtener_especialidades_admin()

    if status == 401:
        return redirigir_por_sesion_vencida()

    if request.method == 'GET':
        medico, error_medico, status = obtener_medico_admin(id_medico)

        if status == 401:
            return redirigir_por_sesion_vencida()

        if error_medico:
            flash(error_medico, 'error')
            return redirect(url_for('admin.listado_medicos'))

        if error:
            flash(error, 'error')

        return renderizar_admin(
            'admin/medicos_form.html', titulo='Editar médico', especialidades=especialidades,
            form=datos_form_medico(medico), edicion=True
        )

    # POST: si algo falla el form vuelve a mostrarse con lo ingresado
    _, error, status = actualizar_medico_admin(id_medico, request.form)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')
        return renderizar_admin(
            'admin/medicos_form.html', titulo='Editar médico', especialidades=especialidades,
            form=request.form.to_dict(), edicion=True
        )

    flash('Médico actualizado correctamente', 'success')
    return redirect(url_for('admin.listado_medicos'))


@admin_bp.route('/medicos/<int:id_medico>/eliminar', methods=['POST'])
def eliminar_medico(id_medico):
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    _, error, status = eliminar_medico_admin(id_medico)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')
    else:
        flash('Médico eliminado correctamente', 'success')

    return redirect(url_for('admin.listado_medicos'))
