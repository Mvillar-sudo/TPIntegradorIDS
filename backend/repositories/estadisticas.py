from db import get_connection
from repositories.consultas_repositories import ejecutar_consulta


def obtener_ausentismo_por_especialidad(desde, hasta):
    consulta = """
        SELECT
            e.id_especialidad,
            e.nombre_especialidad,
            SUM(CASE WHEN t.estado = 'ausente' THEN 1 ELSE 0 END) AS turnos_ausentes,
            SUM(CASE WHEN t.estado = 'atendido' THEN 1 ELSE 0 END) AS turnos_atendidos
        FROM especialidades e
        LEFT JOIN medicos m ON m.id_especialidad = e.id_especialidad
        LEFT JOIN turnos t
            ON t.id_medico = m.id_medico
            AND t.fecha_hora >= %s
            AND t.fecha_hora < %s
            AND t.estado IN ('ausente', 'atendido')
        GROUP BY e.id_especialidad, e.nombre_especialidad
        ORDER BY e.nombre_especialidad
    """
    return ejecutar_consulta(consulta, (desde, hasta))


def obtener_ocupacion_por_consultorio(desde, hasta):
    consulta = """
        SELECT
            c.id_consultorio,
            c.numero_consultorio,
            c.piso,
            COUNT(t.id_turno) AS total_turnos_generados,
            SUM(CASE
                WHEN t.estado IN ('reservado', 'confirmado', 'atendido', 'ausente') THEN 1
                ELSE 0
            END) AS turnos_ocupados
        FROM consultorios c
        LEFT JOIN turnos t
            ON t.id_consultorio = c.id_consultorio
            AND t.fecha_hora >= %s
            AND t.fecha_hora < %s
        GROUP BY c.id_consultorio, c.numero_consultorio, c.piso
        ORDER BY c.numero_consultorio
    """
    return ejecutar_consulta(consulta, (desde, hasta))