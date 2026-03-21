from flask import Blueprint, jsonify, request, render_template
from flask_login import current_user, logout_user, login_required

from app.controllers import banktransfer_controller as controller
from app.models.banktransfer import BankTransfer

banktransfer_bp = Blueprint('banktransfer', __name__, url_prefix='/banktransfer')

@banktransfer_bp.route('/create', methods=['POST'])
@login_required
def create():
    try:
       return controller.create_banktransfer()
    except Exception as e:
        raise e
    
@banktransfer_bp.route('/update/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
       return controller.update_banktransfer(id)
    except Exception as e:
        raise e
    
@banktransfer_bp.route('/delete/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
       return controller.delete_banktransfer(id)
    except Exception as e:
        raise e
    
@banktransfer_bp.route('/get/record/<int:id>', methods=['GET'])
@login_required
def get_record(id):
    try:
        return controller.get_record(id)
    except Exception as e:
        raise e