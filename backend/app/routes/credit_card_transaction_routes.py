from flask import Blueprint

from app.controllers import cashledger_controller as controller
from app.routes._rest import register

credit_card_ledger_bp = Blueprint('credit_card_ledger', __name__)


# JSON: GET /api/card_ledger, GET /api/card_ledger/<id>
register(credit_card_ledger_bp, controller.CARD, '/card_ledger')
