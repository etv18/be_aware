from flask import Blueprint

from app.controllers import loan_payment_controller as controller
from app.routes._rest import register

loan_payment_bp = Blueprint('loan_payment', __name__)


# JSON: GET /api/loan_payments, POST /api/loan_payments, GET /api/loan_payments/<id>, PUT /api/loan_payments/<id>, DELETE /api/loan_payments/<id>
register(loan_payment_bp, controller.RESOURCE, '/loan_payments')
