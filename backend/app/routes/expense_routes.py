from flask import Blueprint

from app.controllers import expense_controller as controller
from app.routes._rest import register

expense_bp = Blueprint('expense', __name__)


# JSON: GET /api/expenses, POST /api/expenses, GET /api/expenses/<id>, PUT /api/expenses/<id>, DELETE /api/expenses/<id>
register(expense_bp, controller.RESOURCE, '/expenses')
