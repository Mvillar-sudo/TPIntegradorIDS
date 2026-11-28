from repositories.consultas_repositories import ejecutar_consulta


def obtener_detalle_turno(id_turno):
    """
    Pre: 'id_turno' es un entero positivo.
    Post: Devuelve un diccionario con los datos del turno, del paciente, del médico, de la
          especialidad y del consultorio necesarios para armar el mail.
          Si el turno no existe o no tiene paciente asignado devuelve None.
    """
    return ejecutar_consulta(
        """
        SELECT t.id_turno, t.fecha_hora, t.token_qr,
               up.nombre_usuario AS paciente_nombre,
               up.apellido_usuario AS paciente_apellido,
               up.email_usuario AS paciente_email,
               um.nombre_usuario AS medico_nombre,
               um.apellido_usuario AS medico_apellido,
               e.nombre_especialidad AS especialidad,
               c.numero_consultorio, c.piso
        FROM turnos AS t
        JOIN usuarios AS up ON up.id_usuario = t.id_paciente
        JOIN medicos AS m ON m.id_medico = t.id_medico
        JOIN usuarios AS um ON um.id_usuario = m.id_usuario
        JOIN especialidades AS e ON e.id_especialidad = m.id_especialidad
        JOIN consultorios AS c ON c.id_consultorio = t.id_consultorio
        WHERE t.id_turno = %s
        """,
        (id_turno,),
        fetch_all=False,
    )
