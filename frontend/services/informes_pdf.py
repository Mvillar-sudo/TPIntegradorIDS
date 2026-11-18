from fpdf import FPDF


def _texto(valor):
    """Convierte un valor a texto que la fuente base del PDF (latin-1) pueda dibujar.

    Las tildes y la ñ entran en latin-1; cualquier otro carácter se reemplaza por '?'.
    Los valores vacíos (por ejemplo un consultorio sin piso) se muestran como '-'.
    """
    if valor is None or valor == '':
        return '-'
    return str(valor).encode('latin-1', 'replace').decode('latin-1')


def _titulo(pdf, texto):
    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, _texto(texto), new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)


def _tabla(pdf, encabezados, filas):
    """Dibuja una tabla. La primera fila (los encabezados) sale en negrita."""
    if not filas:
        pdf.cell(0, 8, 'No hay datos para el período', new_x='LMARGIN', new_y='NEXT')
        return

    with pdf.table(text_align='CENTER') as tabla:
        fila = tabla.row()
        for encabezado in encabezados:
            fila.cell(_texto(encabezado))

        for datos_fila in filas:
            fila = tabla.row()
            for valor in datos_fila:
                fila.cell(_texto(valor))


def generar_pdf_informes(datos, desde, hasta):
    """Arma el PDF con los dos informes del backend.

    Pre: 'datos' es la respuesta de /estadisticas; 'desde' y 'hasta' son strings YYYY-MM-DD.
    Post: Devuelve los bytes del PDF.
    """
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Centro Médico Salud Integral', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, _texto(f'Informes del {desde} al {hasta}'), new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    _titulo(pdf, 'Ausentismo por especialidad')
    _tabla(
        pdf,
        ['Especialidad', 'Atendidos', 'Ausentes', '% ausentismo'],
        [
            [f['nombre_especialidad'], f['turnos_atendidos'], f['turnos_ausentes'],
             f"{f['porcentaje_ausentismo']}%"]
            for f in datos.get('ausentismo_por_especialidad', [])
        ],
    )
    pdf.ln(8)

    _titulo(pdf, 'Ocupación por consultorio')
    _tabla(
        pdf,
        ['Consultorio', 'Piso', 'Generados', 'Ocupados', '% ocupación'],
        [
            [f['numero_consultorio'], f['piso'], f['total_turnos_generados'],
             f['turnos_ocupados'], f"{f['porcentaje_ocupacion']}%"]
            for f in datos.get('ocupacion_por_consultorio', [])
        ],
    )

    return bytes(pdf.output())
