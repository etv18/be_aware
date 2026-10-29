from flask import Blueprint
from flask_login import login_required

from app.controllers import cashledger_controller as controller
from app.routes._pages import page
from app.routes._rest import register

cashlegder_bp = Blueprint('cashledger', __name__, url_prefix='/cashledger')


@cashlegder_bp.route('/index')
@login_required
def index():
    return page('cash', 'cash-ledger', 'Cash ledger')


# POST makes a manual adjustment, DELETE removes one; the other entries are written by the money services
register(cashlegder_bp, controller.CASH)
