from flask import Blueprint
from flask_login import login_required

from app.controllers import credit_card_payment_controller as controller
from app.routes._rest import register

credit_card_payment_bp = Blueprint('credit_card_payment', __name__, url_prefix='/credit_card_payments')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(credit_card_payment_bp, controller.RESOURCE)
