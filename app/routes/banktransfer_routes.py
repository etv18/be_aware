from flask import Blueprint
from flask_login import login_required

from app.controllers import banktransfer_controller as controller
from app.routes._rest import register

banktransfer_bp = Blueprint('banktransfer', __name__, url_prefix='/banktransfer')

# GET /, POST /, GET /<id>, PUT /<id>, DELETE /<id>   (JSON in, JSON out)
register(banktransfer_bp, controller.RESOURCE)
