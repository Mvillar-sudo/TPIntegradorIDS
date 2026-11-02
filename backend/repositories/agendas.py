from datetime import datetime, timedelta

from ..constants import MAX_ESPACIOS_GENERADOS
from ..consultas_repositories import ejecutar_consulta, get_connection


def listar_agendas():
    return ejecutar_consulta("""
     SELECT a.id_agenda, a.id_medico, m.nombre_medico,
         m.apellido_medico, a.id_consultorio, c.numero_consultorio,
         c.piso, a.agenda_fecha_hora_inicio, a.agenda_fecha_hora_fin
        FROM agendas AS a
        JOIN medicos AS m ON m.id_medico = a.id_medico
        JOIN consultorios AS c ON c.id_consultorio = a.id_consultorio
     ORDER BY a.id_medico, a.agenda_fecha_hora_inicio
    """)


def crear_agenda(values):
    connection = get_connection()
    if not connection:
        raise RuntimeError('No se pudo conectar a la base de datos')

    cursor = connection.cursor()
    try:
        cursor.execute(
            'SELECT id_consultorio FROM consultorios WHERE id_consultorio = %s FOR UPDATE',
            (values['id_consultorio'],),
        )
        if not cursor.fetchone():
            raise ValueError('El consultorio indicado no existe')
        cursor.execute(
            'SELECT id_medico FROM medicos WHERE id_medico = %s FOR UPDATE',
            (values['id_medico'],),
        )
        if not cursor.fetchone():
            raise ValueError('El médico indicado no existe')

        cursor.execute("""
            SELECT a.id_agenda
            FROM agendas AS a
            WHERE a.agenda_fecha_hora_inicio < %s
              AND a.agenda_fecha_hora_fin > %s
              AND (a.id_consultorio = %s OR a.id_medico = %s)
            LIMIT 1
        """, (
            values['agenda_fecha_hora_fin'], values['agenda_fecha_hora_inicio'],
            values['id_consultorio'], values['id_medico'],
        ))
        if cursor.fetchone():
            raise ValueError('El médico o consultorio ya tiene una agenda superpuesta')

        cursor.execute("""
            INSERT INTO agendas
                (id_medico, id_consultorio, agenda_fecha_hora_inicio,
                 agenda_fecha_hora_fin)
            VALUES (%s, %s, %s, %s)
        """, (
            values['id_medico'], values['id_consultorio'],
            values['agenda_fecha_hora_inicio'], values['agenda_fecha_hora_fin'],
        ))
        agenda_id = cursor.lastrowid

        now = datetime.now()
        slot_duration = timedelta(minutes=values['duracion_turno_minutos'])
        created_count = 0
        slot_start = values['agenda_fecha_hora_inicio']
        schedule_end = values['agenda_fecha_hora_fin']
        while slot_start + slot_duration <= schedule_end:
            if slot_start > now:
                cursor.execute("""
                    INSERT INTO turnos
                        (id_medico, id_paciente, id_consultorio, fecha_hora, estado)
                    VALUES (%s, NULL, %s, %s, 'disponible')
                """, (values['id_medico'], values['id_consultorio'], slot_start))
                created_count += 1
                if created_count > MAX_ESPACIOS_GENERADOS:
                    raise ValueError('El período generaría más de 10.000 turnos')
            slot_start += slot_duration

        if created_count == 0:
            raise ValueError('El período no contiene turnos futuros')
        connection.commit()
        return agenda_id, created_count
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

def crear_agenda(values):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        id_consultorio = values['id_consultorio']
        id_medico = values['id_medico']
        inicio = values['agenda_fecha_hora_inicio']
        fin = values['agenda_fecha_hora_fin']
        duracion = timedelta(minutes=values['duracion_turno_minutos'])

        cursor.execute(
            'SELECT id_consultorio FROM consultorios WHERE id_consultorio = %s FOR UPDATE',
            (id_consultorio,)
        )
        if not cursor.fetchone():
            raise ValueError('El consultorio indicado no existe')

        cursor.execute(
            'SELECT id_medico FROM medicos WHERE id_medico = %s FOR UPDATE',
            (id_medico,)
        )
        if not cursor.fetchone():
            raise ValueError('El médico indicado no existe')

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

        cursor.execute("""
            INSERT INTO agendas
                (id_medico, id_consultorio, agenda_fecha_hora_inicio,
                 agenda_fecha_hora_fin)
            VALUES (%s, %s, %s, %s)
        """, (id_medico, id_consultorio, inicio, fin))

        agenda_id = cursor.lastrowid

        now = datetime.now()
        slot_start = inicio
        created_count = 0

        while slot_start + duracion <= fin:
            if slot_start > now:
                cursor.execute("""
                    INSERT INTO turnos
                        (id_medico, id_paciente, id_consultorio, fecha_hora, estado)
                    VALUES (%s, NULL, %s, %s, 'disponible')
                """, (id_medico, id_consultorio, slot_start))

                created_count += 1

                if created_count > MAX_ESPACIOS_GENERADOS:
                    raise ValueError('El período generaría más de 10.000 turnos')

            slot_start += duracion

        if created_count == 0:
            raise ValueError('El período no contiene turnos futuros')

        connection.commit()

        cursor.close()
        connection.close()

        return agenda_id, created_count

    except Exception:
        connection.rollback()
        cursor.close()
        connection.close()
        raise