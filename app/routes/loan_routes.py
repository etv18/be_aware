from flask import Blueprint
from flask_login import login_required

from app.controllers import loan_controller as controller
from app.routes._pages import page
from app.routes._rest import register

loan_bp = Blueprint('loan', __name__, url_prefix='/loans')


@loan_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('loans', 'loans', 'Loans')


@loan_bp.route('/associated_records/<int:loan_id>', methods=['GET'])
@login_required
def associated_records(loan_id):
    return page('loans', 'loan', 'Loan', id=loan_id)


register(loan_bp, controller.RESOURCE)

# the payments made on one loan
loan_bp.add_url_rule('/<int:loan_id>/payments', 'payments', login_required(controller.payments_of), methods=['GET'])
