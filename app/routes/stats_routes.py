from flask import Blueprint
from flask_login import login_required

from app.controllers import stats_controller as controller

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

# GET only; ?year=2026 picks the year (this year when missing)
for rule, view in [
    ('/yearly', controller.yearly_report),                      # ?model=expenses|incomes|...
    ('/yearly/all', controller.yearly_all_report),
    ('/incomings-and-outgoings', controller.incomings_and_outgoings),
    ('/incomings-and-outgoings/monthly', controller.incomings_and_outgoings_monthly),
    ('/cash-flow', controller.cash_flow_report),
    ('/sources/bank-accounts', controller.bank_accounts_by_source),
    ('/sources/credit-cards', controller.credit_cards_by_source),
    ('/sources/cash', controller.cash_by_source),
]:
    stats_bp.add_url_rule(rule, view.__name__, login_required(view), methods=['GET'])
