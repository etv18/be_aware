from flask import Blueprint

from app.controllers import bank_account_controller as controller
from app.controllers.out import AccountCashFlowOut, BankAccountRecordsOut
from app.routes._rest import get, register

bank_account_bp = Blueprint('bank_account', __name__)


# JSON: GET /api/bank_accounts, POST /api/bank_accounts, GET /api/bank_accounts/<id>, PUT /api/bank_accounts/<id>, DELETE /api/bank_accounts/<id>
register(bank_account_bp, controller.RESOURCE, '/bank_accounts')

# what hangs from an account, and its reports (GET, ?year=2026)
get(bank_account_bp, '/bank_accounts/<int:account_id>/records', controller.records_of, 'records', out=BankAccountRecordsOut)
get(bank_account_bp, '/bank_accounts/<int:account_id>/reports/yearly', controller.yearly_report, 'yearly', query=('year',))
get(bank_account_bp, '/bank_accounts/<int:account_id>/reports/cash_flow', controller.cash_flow_report, 'cash_flow', out=AccountCashFlowOut, query=('year',))
get(bank_account_bp, '/bank_accounts/<int:account_id>/reports/monthly', controller.monthly_report, 'monthly')
