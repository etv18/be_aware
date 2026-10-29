from flask import Blueprint
from flask_login import login_required

from app.controllers import loan_payment_controller as controller
from app.routes._pages import page
from app.routes._rest import register

loan_payment_bp = Blueprint('loan_payment', __name__, url_prefix='/loan_payments')


@loan_payment_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('loans', 'loan-payments', 'Loan payments')


register(loan_payment_bp, controller.RESOURCE)
