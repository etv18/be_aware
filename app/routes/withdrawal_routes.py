from flask import Blueprint, jsonify, request, render_template

from app.models.withdrawal import Withdrawal

withdrawal_bp = Blueprint('withdrawal', __name__, url_prefix='/withdrawals')

@withdrawal_bp.route('index', methods=['GET'])
def index():
    #withdrawals = Withdrawal.query.all()
    context = {
        #'withdrawals': withdrawals,
    }
    return render_template('withdrawals/index.html')