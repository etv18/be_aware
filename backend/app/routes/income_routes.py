from flask import Blueprint

from app.controllers import income_controller as controller
from app.routes._rest import register

income_bp = Blueprint('income', __name__)


# JSON: GET /api/incomes, POST /api/incomes, GET /api/incomes/<id>, PUT /api/incomes/<id>, DELETE /api/incomes/<id>
register(income_bp, controller.RESOURCE, '/incomes')
