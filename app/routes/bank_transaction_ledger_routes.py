from flask import Blueprint
from flask_login import login_required

from app.controllers import cashledger_controller as controller
from app.routes._pages import page
from app.routes._rest import register

bank_transaction_ledger_bp = Blueprint('bank_transaction_ledger', __name__, url_prefix='/bank_transaction_ledger')


@bank_transaction_ledger_bp.route('/index')
@login_required
def index():
    return page('accounts', 'bank-ledger', 'Bank ledger')


register(bank_transaction_ledger_bp, controller.BANK)
