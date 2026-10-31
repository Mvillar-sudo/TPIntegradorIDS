from flask import Blueprint, request, jsonify
from werkzeug import generate_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/login", methods=['POST'])
def login():
    pass

@auth_bp.route("/auth/register", methods=['POST'])
def crear_paciente():
    pass