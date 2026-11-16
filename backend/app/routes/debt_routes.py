from flask import Blueprint

from app.controllers import debt_controller as controller
from app.controllers.out import DebtPaymentOut
from app.routes._rest import get, register

debt_bp = Blueprint('debt', __name__)


# JSON: GET /api/debts, POST /api/debts, GET /api/debts/<id>, PUT /api/debts/<id>, DELETE /api/debts/<id>
register(debt_bp, controller.RESOURCE, '/debts')

# the payments made on one debt
get(debt_bp, '/debts/<int:debt_id>/payments', controller.payments_of, 'payments', out=DebtPaymentOut, many=True)
