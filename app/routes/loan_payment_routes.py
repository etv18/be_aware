from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import loan_payment_controller as controller
from app.routes._rest import register

loan_payment_bp = Blueprint('loan_payment', __name__)


@loan_payment_bp.get('/loan_payments')
@login_required
def index():
    return render_template('loan_payments.html', nav='loans')


# JSON: GET /api/loan_payments, POST /api/loan_payments, GET /api/loan_payments/<id>, PUT /api/loan_payments/<id>, DELETE /api/loan_payments/<id>
register(loan_payment_bp, controller.RESOURCE, '/loan_payments')
