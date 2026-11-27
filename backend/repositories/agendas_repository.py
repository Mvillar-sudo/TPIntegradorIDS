from consultas_repositories import get_connection, ejecutar_consulta

def listar_agendas():
    """
    Obtiene todas las agendas configuradas haciendo los JOINs correspondientes
    según el esquema de la base de datos (usuarios, medicos, consultorios).
    """
    return ejecutar_consulta("""
        SELECT a.id_agenda, a.id_medico, u.nombre_usuario AS nombre_medico,
               u.apellido_usuario AS apellido_medico, a.id_consultorio, 
               c.numero_consultorio, c.piso, 
               a.agenda_fecha_hora_inicio, a.agenda_fecha_hora_fin
        FROM agendas AS a
        JOIN medicos AS m ON m.id_medico = a.id_medico
        JOIN usuarios AS u ON u.id_usuario = m.id_usuario
        JOIN consultorios AS c ON c.id_consultorio = a.id_consultorio
        ORDER BY a.id_medico, a.agenda_fecha_hora_inicio
    """)


def guardar_agenda_y_turnos(id_medico, id_consultorio, inicio, fin, lista_turnos):
    """
    Abre una transacción para validar la existencia de médico/consultorio,
    comprobar superposiciones, crear la agenda e insertar todos los turnos
    de forma masiva (bulk insert).
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # 1. Validar existencia del consultorio aplicando bloqueo (FOR UPDATE)
        cursor.execute(
            'SELECT id_consultorio FROM consultorios WHERE id_consultorio = %s FOR UPDATE',
            (id_consultorio,)
        )
        if not cursor.fetchone():
            raise ValueError('El consultorio indicado no existe')

        # 2. Validar existencia del médico aplicando bloqueo (FOR UPDATE)
        cursor.execute(
            'SELECT id_medico FROM medicos WHERE id_medico = %s FOR UPDATE',
            (id_medico,)
        )
        if not cursor.fetchone():
            raise ValueError('El médico indicado no existe')

        # 3. Validar que no haya superposición de horarios para ese médico o consultorio
        cursor.execute("""
            SELECT id_agenda
            FROM agendas
            WHERE agenda_fecha_hora_inicio < %s
              AND agenda_fecha_hora_fin > %s
              AND (id_consultorio = %s OR id_medico = %s)
            LIMIT 1
        """, (fin, inicio, id_consultorio, id_medico))

        if cursor.fetchone():
            raise ValueError('El médico o consultorio ya tiene una agenda superpuesta')

        # 4. Insertar la agenda principal
        cursor.execute("""
            INSERT INTO agendas
                (id_medico, id_consultorio, agenda_fecha_hora_inicio, agenda_fecha_hora_fin)
            VALUES (%s, %s, %s, %s)
        """, (id_medico, id_consultorio, inicio, fin))
        
        agenda_id = cursor.lastrowid

        # 5. Insertar los turnos masivamente con un único llamado a la base de datos
        query_turnos = """
            INSERT INTO turnos
                (id_medico, id_consultorio, fecha_hora, estado)
            VALUES (%s, %s, %s, 'disponible')
        """
        # Convertimos la lista de objetos datetime en la lista de tuplas necesaria
        valores_turnos = [(id_medico, id_consultorio, turno) for turno in lista_turnos]
        
        cursor.executemany(query_turnos, valores_turnos)

        # Confirmar la transacción
        connection.commit()
        return agenda_id, cursor.rowcount

    except Exception:
        # Revertir cualquier cambio si algo falla o se lanza un ValueError
        connection.rollback()
        raise
    finally:
        # Liberar recursos
        cursor.close()
        connection.close()