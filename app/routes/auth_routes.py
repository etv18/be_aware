from flask import Blueprint, render_template
from app.extensions import limiter

from app.controllers import auth_controller as controller

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
@limiter.limit('60 per minute')
@limiter.limit('20 per hour')
def login():
    return controller.authenticate_user()

@auth.route('/login', methods=['GET'])
@limiter.limit('60 per minute')
@limiter.limit('20 per hour')
def get_login():
    return render_template('auth/login.html')