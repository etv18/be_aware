from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import deposit_controller as controller
from app.routes._rest import register

deposit_bp = Blueprint('deposit', __name__)


@deposit_bp.get('/deposits')
@login_required
def index():
    return render_template('deposits.html', nav='deposits')


# JSON: GET /api/deposits, POST /api/deposits, GET /api/deposits/<id>, PUT /api/deposits/<id>, DELETE /api/deposits/<id>
register(deposit_bp, controller.RESOURCE, '/deposits')
