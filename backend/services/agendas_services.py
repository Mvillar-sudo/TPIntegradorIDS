from datetime import datetime, timedelta
from constants import MAX_ESPACIOS_GENERADOS
import repositories.agendas_repository as agendas_repository # El archivo del paso anterior con el INSERT masivo

def crear(values):
    """
    Recibe los datos validados. Calcula los intervalos de tiempo en memoria
    (lista de turnos) y pasa el resultado al repositorio para guardarlo.
    """
    inicio = values['agenda_fecha_hora_inicio']
    fin = values['agenda_fecha_hora_fin']
    duracion = timedelta(minutes=values['duracion_turno_minutos'])
    
    now = datetime.now()
    slot_start = inicio
    lista_turnos = []
    
    # Cálculo de los intervalos
    while slot_start + duracion <= fin:
        if slot_start > now:
            lista_turnos.append(slot_start)
        slot_start += duracion

    # Validaciones de negocio post-cálculo
    if not lista_turnos:
        raise ValueError("El período no contiene turnos futuros")
        
    if len(lista_turnos) > MAX_ESPACIOS_GENERADOS:
        raise ValueError(f"El período generaría más de {MAX_ESPACIOS_GENERADOS} turnos")

    # Pasar el resultado al repositorio para guardarlo
    agenda_id, turnos_creados = agendas_repository.guardar_agenda_y_turnos(
        values['id_medico'], 
        values['id_consultorio'], 
        inicio, 
        fin, 
        lista_turnos
    )
    
    return agenda_id, turnos_creados