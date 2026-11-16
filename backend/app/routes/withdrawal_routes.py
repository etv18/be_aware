from flask import Blueprint

from app.controllers import withdrawal_controller as controller
from app.routes._rest import register

withdrawal_bp = Blueprint('withdrawal', __name__)


# JSON: GET /api/withdrawals, POST /api/withdrawals, GET /api/withdrawals/<id>, PUT /api/withdrawals/<id>, DELETE /api/withdrawals/<id>
register(withdrawal_bp, controller.RESOURCE, '/withdrawals')
