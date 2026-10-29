from flask import Blueprint
from flask_login import login_required

from app.controllers import debt_controller as controller
from app.routes._pages import page
from app.routes._rest import register

debt_bp = Blueprint('debt', __name__, url_prefix='/debts')


@debt_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('debts', 'debts', 'Debts')


@debt_bp.route('/associated/records/<int:id>', methods=['GET'])
@login_required
def associated_records(id):
    return page('debts', 'debt', 'Debt', id=id)


register(debt_bp, controller.RESOURCE)

# the payments made on one debt
debt_bp.add_url_rule('/<int:debt_id>/payments', 'payments', login_required(controller.payments_of), methods=['GET'])
