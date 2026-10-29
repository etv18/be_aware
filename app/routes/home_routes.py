from flask import Blueprint
from flask_login import login_required

from app.controllers import home_controller
from app.routes._pages import page

home_bp = Blueprint('home', __name__)


@home_bp.route('/', methods=['GET'])
@login_required
def index():
    return page('home', 'home', 'Home')


@home_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return home_controller.dashboard()


@home_bp.route('/options', methods=['GET'])
@login_required
def options():
    return home_controller.options()
