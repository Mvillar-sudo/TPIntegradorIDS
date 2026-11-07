from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from services.agendas import crear_agenda, obtener_medicos

# Creamos el Blueprint para las rutas de admin del frontend
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/agendas/nueva', methods=['GET', 'POST'])
def nueva_agenda():
    # --- MÉTODO GET: Mostrar el formulario ---
    usuario_actual = session.get('usuario') 

    if request.method == 'GET':
        try:
            lista_medicos = obtener_medicos()
            return render_template(
                'configurar_agenda.html', 
                medicos=lista_medicos,
                usuario=usuario_actual # Pasamos el usuario al HTML
            )
        except Exception as e:
            flash('Error al cargar datos', 'danger')
            return render_template('configurar_agenda.html', medicos=[], usuario=usuario_actual)

    # --- MÉTODO POST: Capturar datos y enviar al backend ---
    if request.method == 'POST':
        try:
            # 1. Capturamos los datos del formulario HTML
            f_inicio = request.form.get("fecha_inicio")
            h_inicio = request.form.get("hora_inicio")
            f_fin = request.form.get("fecha_fin")
            h_fin = request.form.get("hora_fin")
            
            # 2. Armamos el diccionario EXACTO que valida tu backend
            datos_backend = {
                "id_medico": int(request.form.get("medico_id")),
                "id_consultorio": 1,  # Valor fijo temporalmente
                "agenda_fecha_hora_inicio": f"{f_inicio} {h_inicio}:00",
                "agenda_fecha_hora_fin": f"{f_fin} {h_fin}:00",
                "duracion_turno_minutos": int(request.form.get("duracion_turno", 60))
            }

            # 3. Enviamos los datos mediante requests (a través de tu servicio)
            crear_agenda(datos_backend)
            
            flash('La agenda se generó correctamente.', 'success')
            return redirect(url_for('admin.nueva_agenda'))
            
        except Exception as e:
            flash(f'Error al crear la agenda: {str(e)}', 'danger')
            return redirect(url_for('admin.nueva_agenda'))