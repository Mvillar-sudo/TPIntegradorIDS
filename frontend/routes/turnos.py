from flask import Blueprint, render_template

turnos_bp = Blueprint('turnos', __name__)


@turnos_bp.route('/mis-turnos', methods=['GET'])
def mis_turnos():
    return render_template('mis_turnos.html')
