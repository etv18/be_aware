from flask import Blueprint, render_template

from app.controllers import bank_account_controller as ba_controller
from app.models.bank_account import BankAccount

bank_account_bp = Blueprint('bank_account', __name__, url_prefix='/bank_accounts')

@bank_account_bp.route('/index', methods=['GET'])
def index():
    return render_template('bank_accounts/index.html')