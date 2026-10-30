from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import loan_controller as controller
from app.routes._rest import get, register

loan_bp = Blueprint('loan', __name__)


@loan_bp.get('/loans')
@login_required
def index():
    return render_template('loans.html', nav='loans')


@loan_bp.get('/loans/<int:record_id>')
@login_required
def show(record_id):
    return render_template('loan.html', nav='loans', id=record_id)


# JSON: GET /api/loans, POST /api/loans, GET /api/loans/<id>, PUT /api/loans/<id>, DELETE /api/loans/<id>
register(loan_bp, controller.RESOURCE, '/loans')

# the payments made on one loan
get(loan_bp, '/loans/<int:loan_id>/payments', controller.payments_of, 'payments')
