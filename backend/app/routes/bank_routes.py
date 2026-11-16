from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import bank_controller as controller
from app.routes._rest import register

bank_bp = Blueprint('bank', __name__)


@bank_bp.get('/banks')
@login_required
def index():
    return render_template('banks.html', nav='banks')


# JSON: GET /api/banks, POST /api/banks, GET /api/banks/<id>, PUT /api/banks/<id>, DELETE /api/banks/<id>
register(bank_bp, controller.RESOURCE, '/banks')
