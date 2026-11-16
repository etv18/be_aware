from flask import Blueprint

from app.controllers import debt_payment_controller as controller
from app.routes._rest import register

debt_payment_bp = Blueprint('debt_payment', __name__)


# JSON: GET /api/debt_payments, POST /api/debt_payments, GET /api/debt_payments/<id>, PUT /api/debt_payments/<id>, DELETE /api/debt_payments/<id>
register(debt_payment_bp, controller.RESOURCE, '/debt_payments')
