from flask import Blueprint

from app.controllers import stats_controller as controller
from app.controllers.out import YearlyReportOut
from app.routes._rest import get

stats_bp = Blueprint('stats', __name__)

# Reports of the whole app. GET only; ?year=2026 picks the year (this year when missing)
for path, view, query, out in [
    ('/reports/yearly', controller.yearly_report, ('model', 'year'), YearlyReportOut),   # ?model=expenses|incomes|...
    ('/reports/yearly/all', controller.yearly_all_report, ('year',), None),
    ('/reports/incomings_and_outgoings', controller.incomings_and_outgoings, ('year',), None),
    ('/reports/incomings_and_outgoings/monthly', controller.incomings_and_outgoings_monthly, (), None),
    ('/reports/cash_flow', controller.cash_flow_report, ('year',), None),
    ('/reports/sources/bank_accounts', controller.bank_accounts_by_source, ('year',), None),
    ('/reports/sources/credit_cards', controller.credit_cards_by_source, ('year',), None),
    ('/reports/sources/cash', controller.cash_by_source, ('year',), None),
]:
    get(stats_bp, path, view, view.__name__, out=out, query=query)
