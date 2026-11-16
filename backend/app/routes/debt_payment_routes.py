from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import debt_payment_controller as controller
from app.routes._rest import register

debt_payment_bp = Blueprint('debt_payment', __name__)


@debt_payment_bp.get('/debt_payments')
@login_required
def index():
    return render_template('debt_payments.html', nav='debts')


# JSON: GET /api/debt_payments, POST /api/debt_payments, GET /api/debt_payments/<id>, PUT /api/debt_payments/<id>, DELETE /api/debt_payments/<id>
register(debt_payment_bp, controller.RESOURCE, '/debt_payments')
