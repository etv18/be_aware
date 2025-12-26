from flask import Blueprint, jsonify, request, render_template

from app.controllers import banktransfer_controller as controller
from app.models.banktransfer import BankTransfer

banktransfer_bp = Blueprint('BankTransfer', __name__, url_prefix='/banktransfer')

@banktransfer_bp.route('/create', methods=['POST'])
def create():
    try:
       return controller.create_banktransfer()
    except Exception as e:
        raise e