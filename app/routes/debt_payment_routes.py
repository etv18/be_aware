from flask import Blueprint
from flask_login import login_required

from app.controllers import debt_payment_controller as controller
from app.routes._pages import page
from app.routes._rest import register

debt_payment_bp = Blueprint('debt_payment', __name__, url_prefix='/debt_payments')


@debt_payment_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('debts', 'debt-payments', 'Debt payments')


register(debt_payment_bp, controller.RESOURCE)
