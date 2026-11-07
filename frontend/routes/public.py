import requests
import os 
from constants import BACKEND_URL
from flask import (request, Blueprint, render_template, flash, redirect, url_for, session)


public_bp = Blueprint("public", __name__)

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/about-us')
def about_us():
    return render_template('about_us.html')