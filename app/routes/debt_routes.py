from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import debt_controller as controller
from app.routes._rest import get, register

debt_bp = Blueprint('debt', __name__)


@debt_bp.get('/debts')
@login_required
def index():
    return render_template('debts.html', nav='debts')


@debt_bp.get('/debts/<int:record_id>')
@login_required
def show(record_id):
    return render_template('debt.html', nav='debts', id=record_id)


# JSON: GET /api/debts, POST /api/debts, GET /api/debts/<id>, PUT /api/debts/<id>, DELETE /api/debts/<id>
register(debt_bp, controller.RESOURCE, '/debts')

# the payments made on one debt
get(debt_bp, '/debts/<int:debt_id>/payments', controller.payments_of, 'payments')
