from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash_messages'

@app.route('/turnos/reserva', methods=['GET', 'POST'])
def reserva():
    # Datos ficticios simulando el JSON del backend
    mock_especialidades = [
        {"id_especialidad": 1, "nombre": "Cardiología"},
        {"id_especialidad": 2, "nombre": "Pediatría"}
    ]
    
    # Diccionario simulando filtrado por id_especialidad
    mock_medicos = {
        "1": [{"id_medico": 101, "nombre": "Dr. Carlos Pérez", "id_consultorio": "102"}],
        "2": [{"id_medico": 102, "nombre": "Dra. Ana Gómez", "id_consultorio": "204"}]
    }
    
    # Diccionario simulando filtrado por id_medico y campo DATETIME
    mock_turnos = {
        "101": [
            {"id_turno": 45, "fecha_hora": "2026-10-27 09:00:00"},
            {"id_turno": 46, "fecha_hora": "2026-10-27 09:20:00"}
        ],
        "102": [
            {"id_turno": 47, "fecha_hora": "2026-10-28 10:00:00"}
        ]
    }

    especialidad_sel = request.form.get('especialidad_id')
    medico_sel = request.form.get('medico_id')
    accion = request.form.get('accion')

    if request.method == 'POST' and accion == 'confirmar':
        id_turno = request.form.get('id_turno')
        flash(f"Reserva confirmada. Turno ID: {id_turno}")
        return redirect(url_for('mis_turnos'))

    # Cargar datos según la selección actual
    medicos = mock_medicos.get(especialidad_sel, []) if especialidad_sel else []
    turnos_disponibles = mock_turnos.get(medico_sel, []) if medico_sel else []

    return render_template(
        'reserva.html',
        especialidades=mock_especialidades,
        medicos=medicos,
        turnos_disponibles=turnos_disponibles,
        especialidad_seleccionada=especialidad_sel,
        medico_seleccionado=medico_sel
    )

@app.route('/mis-turnos')
def mis_turnos():
    return "¡Reserva simulada con éxito! Aquí renderizaremos el QR."

if __name__ == '__main__':
    app.run(port=5000, debug=True)