from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import cashledger_controller as controller
from app.routes._rest import register

bank_transaction_ledger_bp = Blueprint('bank_transaction_ledger', __name__)


@bank_transaction_ledger_bp.get('/bank_ledger')
@login_required
def index():
    return render_template('bank_ledger.html', nav='accounts')


# JSON: GET /api/bank_ledger, GET /api/bank_ledger/<id>
register(bank_transaction_ledger_bp, controller.BANK, '/bank_ledger')
