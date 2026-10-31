from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import expense_controller as controller
from app.routes._rest import register

expense_bp = Blueprint('expense', __name__)


@expense_bp.get('/expenses')
@login_required
def index():
    return render_template('expenses.html', nav='expenses')


# JSON: GET /api/expenses, POST /api/expenses, GET /api/expenses/<id>, PUT /api/expenses/<id>, DELETE /api/expenses/<id>
register(expense_bp, controller.RESOURCE, '/expenses')
