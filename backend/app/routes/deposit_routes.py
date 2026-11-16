from flask import Blueprint

from app.controllers import deposit_controller as controller
from app.routes._rest import register

deposit_bp = Blueprint('deposit', __name__)


# JSON: GET /api/deposits, POST /api/deposits, GET /api/deposits/<id>, PUT /api/deposits/<id>, DELETE /api/deposits/<id>
register(deposit_bp, controller.RESOURCE, '/deposits')
