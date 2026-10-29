from flask import Blueprint
from flask_login import login_required

from app.controllers import withdrawal_controller as controller
from app.routes._pages import page
from app.routes._rest import register

withdrawal_bp = Blueprint('withdrawal', __name__, url_prefix='/withdrawals')


@withdrawal_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('withdrawals', 'withdrawals', 'Withdrawals')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(withdrawal_bp, controller.RESOURCE)
