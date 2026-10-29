from flask import Blueprint
from flask_login import login_required

from app.controllers import expense_controller as controller
from app.routes._pages import page
from app.routes._rest import register

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')


@expense_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('expenses', 'expenses', 'Expenses')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(expense_bp, controller.RESOURCE)
