from flask import Blueprint

from app.controllers import credit_card_payment_controller as controller
from app.routes._rest import register

credit_card_payment_bp = Blueprint('credit_card_payment', __name__)

# JSON only: GET /api/credit_card_payments, POST /api/credit_card_payments, GET /api/credit_card_payments/<id>, PUT /api/credit_card_payments/<id>, DELETE /api/credit_card_payments/<id>
register(credit_card_payment_bp, controller.RESOURCE, '/credit_card_payments')
