from flask import Blueprint

from app.controllers import cashledger_controller as controller
from app.routes._rest import register

cash_ledger_bp = Blueprint('cashledger', __name__)


# JSON: GET /api/cash_ledger, GET /api/cash_ledger/<id>; POST makes a manual adjustment, DELETE removes one (the other entries are written by the money services)
register(cash_ledger_bp, controller.CASH, '/cash_ledger')
