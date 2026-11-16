from flask import Blueprint

from app.controllers import loan_controller as controller
from app.controllers.out import LoanPaymentOut
from app.routes._rest import get, register

loan_bp = Blueprint('loan', __name__)


# JSON: GET /api/loans, POST /api/loans, GET /api/loans/<id>, PUT /api/loans/<id>, DELETE /api/loans/<id>
register(loan_bp, controller.RESOURCE, '/loans')

# the payments made on one loan
get(loan_bp, '/loans/<int:loan_id>/payments', controller.payments_of, 'payments', out=LoanPaymentOut, many=True)
