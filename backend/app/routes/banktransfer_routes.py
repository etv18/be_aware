from flask import Blueprint

from app.controllers import banktransfer_controller as controller
from app.routes._rest import register

banktransfer_bp = Blueprint('banktransfer', __name__)

# JSON only: GET /api/bank_transfers, POST /api/bank_transfers, GET /api/bank_transfers/<id>, PUT /api/bank_transfers/<id>, DELETE /api/bank_transfers/<id>
register(banktransfer_bp, controller.RESOURCE, '/bank_transfers')
