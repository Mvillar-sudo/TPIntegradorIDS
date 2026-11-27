from flask import Blueprint, render_template, request

errores_bp = Blueprint('errores', __name__)

# Secciones del menú que todavía no están hechas: se avisa en vez de mostrar un error.
# Cuando una sección exista, su ruta se atiende antes y esta lista ya no la alcanza.
SECCIONES_EN_CONSTRUCCION = ('/turnos', '/medicos', '/especialidades')


@errores_bp.app_errorhandler(404)
def pagina_no_encontrada(error):
    """
    Pre: -
    Post: Muestra una página de error con el diseño del sitio. Si la dirección es una sección del
          menú que todavía no está hecha, avisa que está en construcción.
    """
    if request.path.rstrip('/') in SECCIONES_EN_CONSTRUCCION:
        return render_template(
            'errores/error.html', codigo=404, titulo='Sección en construcción',
            mensaje='Esta parte del sitio todavía no está disponible. Estamos trabajando en ella.'
        ), 404

    return render_template(
        'errores/error.html', codigo=404, titulo='No encontramos esa página',
        mensaje='Puede que el link esté mal escrito o que la página ya no exista.'
    ), 404


@errores_bp.app_errorhandler(403)
def sin_permiso(error):
    """
    Pre: -
    Post: Muestra una página de error con el diseño del sitio para quien no tiene permiso.
    """
    return render_template(
        'errores/error.html', codigo=403, titulo='No tenés permiso para ver esta página',
        mensaje='Esta sección es solo para otros tipos de usuario. Si creés que es un error, '
                'iniciá sesión con otra cuenta.'
    ), 403


@errores_bp.app_errorhandler(500)
def error_del_servidor(error):
    """
    Pre: -
    Post: Muestra una página de error con el diseño del sitio cuando algo falla en el servidor.
    """
    return render_template(
        'errores/error.html', codigo=500, titulo='Algo salió mal',
        mensaje='Hubo un problema de nuestro lado. Probá de nuevo en unos minutos.'
    ), 500
