from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import withdrawal_controller as controller
from app.routes._rest import register

withdrawal_bp = Blueprint('withdrawal', __name__)


@withdrawal_bp.get('/withdrawals')
@login_required
def index():
    return render_template('withdrawals.html', nav='withdrawals')


# JSON: GET /api/withdrawals, POST /api/withdrawals, GET /api/withdrawals/<id>, PUT /api/withdrawals/<id>, DELETE /api/withdrawals/<id>
register(withdrawal_bp, controller.RESOURCE, '/withdrawals')
