from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import bank_account_controller as controller
from app.routes._rest import get, register

bank_account_bp = Blueprint('bank_account', __name__)


@bank_account_bp.get('/bank_accounts')
@login_required
def index():
    return render_template('bank_accounts.html', nav='accounts')


@bank_account_bp.get('/bank_accounts/<int:record_id>')
@login_required
def show(record_id):
    return render_template('bank_account.html', nav='accounts', id=record_id)


# JSON: GET /api/bank_accounts, POST /api/bank_accounts, GET /api/bank_accounts/<id>, PUT /api/bank_accounts/<id>, DELETE /api/bank_accounts/<id>
register(bank_account_bp, controller.RESOURCE, '/bank_accounts')

# what hangs from an account, and its reports (GET, ?year=2026)
get(bank_account_bp, '/bank_accounts/<int:account_id>/records', controller.records_of, 'records')
get(bank_account_bp, '/bank_accounts/<int:account_id>/reports/yearly', controller.yearly_report, 'yearly')
get(bank_account_bp, '/bank_accounts/<int:account_id>/reports/cash_flow', controller.cash_flow_report, 'cash_flow')
get(bank_account_bp, '/bank_accounts/<int:account_id>/reports/monthly', controller.monthly_report, 'monthly')
