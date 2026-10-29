from flask import Blueprint
from flask_login import login_required

from app.controllers import bank_controller as controller
from app.routes._pages import page
from app.routes._rest import register

bank_bp = Blueprint('bank', __name__, url_prefix='/banks')


@bank_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('banks', 'banks', 'Banks')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(bank_bp, controller.RESOURCE)
