from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import auth_controller as controller
from app.extensions import limiter

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def get_login():
    return render_template('auth/login.html')


@auth.route('/login', methods=['POST'])
@limiter.limit('20 per hour;60 per minute')
def login():
    return controller.login()


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    return controller.logout()


@auth.route('/session', methods=['GET'])
def session_info():
    return controller.session_info()
