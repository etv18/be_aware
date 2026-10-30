from flask import Blueprint

from app.controllers import stats_controller as controller
from app.routes._rest import get

stats_bp = Blueprint('stats', __name__)

# Reports of the whole app. GET only; ?year=2026 picks the year (this year when missing)
for path, view in [
    ('/reports/yearly', controller.yearly_report),                      # ?model=expenses|incomes|...
    ('/reports/yearly/all', controller.yearly_all_report),
    ('/reports/incomings_and_outgoings', controller.incomings_and_outgoings),
    ('/reports/incomings_and_outgoings/monthly', controller.incomings_and_outgoings_monthly),
    ('/reports/cash_flow', controller.cash_flow_report),
    ('/reports/sources/bank_accounts', controller.bank_accounts_by_source),
    ('/reports/sources/credit_cards', controller.credit_cards_by_source),
    ('/reports/sources/cash', controller.cash_by_source),
]:
    get(stats_bp, path, view, view.__name__)
