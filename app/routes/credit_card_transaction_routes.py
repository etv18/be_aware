from flask import Blueprint
from flask_login import login_required

from app.controllers import cashledger_controller as controller
from app.routes._pages import page
from app.routes._rest import register

credit_card_ledger_bp = Blueprint('credit_card_ledger', __name__, url_prefix='/credit_card_ledger')


@credit_card_ledger_bp.route('/ledger')
@login_required
def index():
    return page('cards', 'card-ledger', 'Card ledger')


register(credit_card_ledger_bp, controller.CARD)
