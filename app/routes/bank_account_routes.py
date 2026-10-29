from flask import Blueprint
from flask_login import login_required

from app.controllers import bank_account_controller as controller
from app.routes._pages import page
from app.routes._rest import register

bank_account_bp = Blueprint('bank_account', __name__, url_prefix='/bank_accounts')


@bank_account_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('accounts', 'bank-accounts', 'Bank accounts')


@bank_account_bp.route('/associated_records/<int:bank_account_id>', methods=['GET'])
@login_required
def associated_records(bank_account_id):
    return page('accounts', 'bank-account', 'Bank account', id=bank_account_id)


register(bank_account_bp, controller.RESOURCE)

# what hangs from an account, and its reports (GET, ?year=2026)
bank_account_bp.add_url_rule('/<int:account_id>/records', 'records', login_required(controller.records_of), methods=['GET'])
bank_account_bp.add_url_rule('/<int:account_id>/reports/yearly', 'yearly', login_required(controller.yearly_report), methods=['GET'])
bank_account_bp.add_url_rule('/<int:account_id>/reports/cash-flow', 'cash_flow', login_required(controller.cash_flow_report), methods=['GET'])
bank_account_bp.add_url_rule('/<int:account_id>/reports/monthly', 'monthly', login_required(controller.monthly_report), methods=['GET'])
