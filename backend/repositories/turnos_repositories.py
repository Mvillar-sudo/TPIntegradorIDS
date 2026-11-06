from db import get_connection


def obtener_turnos_disponibles(medico_id=None, fecha=None, especialidad_id=None):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT
                t.id_turno,
                t.id_medico,
                u.nombre_usuario AS nombre_medico,
                u.apellido_usuario AS apellido_medico,
                e.id_especialidad,
                e.nombre_especialidad,
                t.id_consultorio,
                c.numero_consultorio,
                c.piso,
                t.fecha_hora,
                t.estado
            FROM turnos t
            INNER JOIN medicos m
                ON t.id_medico = m.id_medico
            INNER JOIN usuarios u
                ON m.id_usuario = u.id_usuario
            INNER JOIN especialidades e
                ON m.id_especialidad = e.id_especialidad
            INNER JOIN consultorios c
                ON t.id_consultorio = c.id_consultorio
            WHERE t.estado = 'disponible'
        """

        parametros = []

        if medico_id is not None:
            query += " AND t.id_medico = %s"
            parametros.append(medico_id)

        if especialidad_id is not None:
            query += " AND e.id_especialidad = %s"
            parametros.append(especialidad_id)

        if fecha is not None:
            query += " AND DATE(t.fecha_hora) = %s"
            parametros.append(fecha)

        query += " ORDER BY t.fecha_hora ASC;"

        cursor.execute(query, tuple(parametros))
        resultados = cursor.fetchall()

        return resultados

    except Exception as e:
        print(f"Error al obtener turnos disponibles: {e}")
        return None

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


def reservar_turno(id_turno, id_paciente, codigo_qr_hash):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        # 1. Consultar el turno.
        query_select = """
            SELECT id_turno, id_medico, fecha_hora, estado
            FROM turnos
            WHERE id_turno = %s;
        """

        cursor.execute(query_select, (id_turno,))
        turno = cursor.fetchone()

        if turno is None:
            return {"estado": "no_encontrado"}

        if turno["estado"] != "disponible":
            return {"estado": "no_disponible"}

        # 2. Reservar el turno.
        query_update = """
            UPDATE turnos
            SET id_paciente = %s,
                estado = 'reservado',
                token_qr = %s
            WHERE id_turno = %s
              AND estado = 'disponible';
        """

        cursor.execute(
            query_update,
            (id_paciente, codigo_qr_hash, id_turno)
        )

        # Comprobar que se haya actualizado una fila.
        if cursor.rowcount != 1:
            conexion.rollback()
            return {"estado": "no_disponible"}

        conexion.commit()

        return {
            "estado": "reservado",
            "turno": turno
        }

    except Exception as e:
        if conexion is not None:
            conexion.rollback()

        print(f"Error al reservar turno: {e}")
        return {"estado": "error"}

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()