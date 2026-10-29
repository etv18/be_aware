from flask import Blueprint
from flask_login import login_required

from app.controllers import income_controller as controller
from app.routes._pages import page
from app.routes._rest import register

income_bp = Blueprint('income', __name__, url_prefix='/incomes')


@income_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('incomes', 'incomes', 'Incomes')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(income_bp, controller.RESOURCE)
