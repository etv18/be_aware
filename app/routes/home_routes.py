from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import home_controller
from app.routes._rest import get

home_bp = Blueprint('home', __name__)


@home_bp.get('/')
@login_required
def index():
    return render_template('home.html', nav='home')


# JSON: the figures of the home page and the lists the forms choose from
get(home_bp, '/dashboard', home_controller.dashboard, 'dashboard')
get(home_bp, '/options', home_controller.options, 'options')
