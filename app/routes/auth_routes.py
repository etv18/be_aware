from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import auth_controller as controller
from app.extensions import limiter

auth = Blueprint('auth', __name__)


@auth.get('/login')
def get_login():
    return render_template('auth/login.html')


# JSON: POST /api/login, POST /api/logout, GET /api/session (who is logged in + the CSRF token)
@auth.post('/api/login')
@limiter.limit('20 per hour;60 per minute')
def login():
    return controller.login()


@auth.post('/api/logout')
@login_required
def logout():
    return controller.logout()


@auth.get('/api/session')
def session_info():
    return controller.session_info()
