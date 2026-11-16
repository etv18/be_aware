from flask import Blueprint

from app.controllers import bank_controller as controller
from app.routes._rest import register

bank_bp = Blueprint('bank', __name__)


# JSON: GET /api/banks, POST /api/banks, GET /api/banks/<id>, PUT /api/banks/<id>, DELETE /api/banks/<id>
register(bank_bp, controller.RESOURCE, '/banks')
