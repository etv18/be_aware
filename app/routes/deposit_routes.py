from flask import Blueprint
from flask_login import login_required

from app.controllers import deposit_controller as controller
from app.routes._pages import page
from app.routes._rest import register

deposit_bp = Blueprint('deposit', __name__, url_prefix='/deposits')


@deposit_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('deposits', 'deposits', 'Deposits')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(deposit_bp, controller.RESOURCE)
