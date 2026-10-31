from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import cashledger_controller as controller
from app.routes._rest import register

credit_card_ledger_bp = Blueprint('credit_card_ledger', __name__)


@credit_card_ledger_bp.get('/card_ledger')
@login_required
def index():
    return render_template('card_ledger.html', nav='cards')


# JSON: GET /api/card_ledger, GET /api/card_ledger/<id>
register(credit_card_ledger_bp, controller.CARD, '/card_ledger')
