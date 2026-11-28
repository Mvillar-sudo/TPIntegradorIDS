from flask import Blueprint, Response, render_template, request, redirect, session, url_for, flash

from datetime import timedelta

from services.tiempo import obtener_ahora_gmt3
from services.agendas import crear_agenda_desde_formulario, obtener_medicos, obtener_consultorios
from services.admin import verificar_admin, renderizar_admin, redirigir_por_sesion_vencida, obtener_estadisticas, obtener_informes_admin, obtener_agendas_admin, eliminar_agenda_admin, obtener_medicos_admin, obtener_especialidades_admin, crear_medico_admin, obtener_medico_admin, actualizar_medico_admin, eliminar_medico_admin, datos_form_medico
from services.informes_pdf import generar_pdf_informes

# Creamos el Blueprint para las rutas de admin del frontend
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/agendas/nueva', methods=['GET', 'POST'])
def nueva_agenda():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    # --- MÉTODO POST: crear la agenda con los datos del formulario ---
    if request.method == 'POST':
        try:
            creadas, errores = crear_agenda_desde_formulario(request.form)
        except ValueError as error:
            flash(f'Error al crear la agenda: {error}', 'danger')
            return redirect(url_for('admin.nueva_agenda'))

        if creadas:
            flash(f'Se crearon {creadas} agenda(s) correctamente.', 'success')
        if errores:
            flash('No se pudieron crear: ' + '; '.join(errores), 'danger')
        return redirect(url_for('admin.nueva_agenda'))

    # --- MÉTODO GET: mostrar el formulario ---
    usuario_actual = session.get('usuario')

    try:
        lista_medicos = obtener_medicos()
        lista_consultorios = obtener_consultorios()
        return render_template(
            'configurar_agenda.html',
            medicos=lista_medicos,
            consultorios=lista_consultorios,
            usuario=usuario_actual
        )
    except ValueError as error:
        flash(str(error), 'danger')
        return render_template('configurar_agenda.html', medicos=[], consultorios=[], usuario=usuario_actual)


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


@admin_bp.route('/informes')
def informes():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    # Por defecto: los últimos 30 días hasta hoy
    hoy = obtener_ahora_gmt3().date()
    desde = request.args.get('desde') or (hoy - timedelta(days=30)).isoformat()
    hasta = request.args.get('hasta') or hoy.isoformat()

    datos, error, status = obtener_informes_admin(desde, hasta)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')

    return renderizar_admin(
        'admin/informes.html', titulo='Informes',
        informes=datos, desde=desde, hasta=hasta
    )


@admin_bp.route('/informes/pdf')
def informes_pdf():
    bloqueo = verificar_admin()
    if bloqueo:
        return bloqueo

    desde = request.args.get('desde', '')
    hasta = request.args.get('hasta', '')

    datos, error, status = obtener_informes_admin(desde, hasta)

    if status == 401:
        return redirigir_por_sesion_vencida()

    if error:
        flash(error, 'error')
        return redirect(url_for('admin.informes', desde=desde, hasta=hasta))

    pdf = generar_pdf_informes(datos, desde, hasta)
    return Response(
        pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=informes_{desde}_{hasta}.pdf'}
    )


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
