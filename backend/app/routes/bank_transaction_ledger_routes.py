from flask import Blueprint

from app.controllers import cashledger_controller as controller
from app.routes._rest import register

bank_transaction_ledger_bp = Blueprint('bank_transaction_ledger', __name__)


# JSON: GET /api/bank_ledger, GET /api/bank_ledger/<id>
register(bank_transaction_ledger_bp, controller.BANK, '/bank_ledger')
