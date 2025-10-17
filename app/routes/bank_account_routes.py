from flask import Blueprint, render_template, redirect, url_for

from app.controllers import bank_account_controller as ba_controller
from app.models.bank_account import BankAccount
from app.models.bank import Bank

bank_account_bp = Blueprint('bank_account', __name__, url_prefix='/bank_accounts')

@bank_account_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.query.all()

    return render_template('bank_accounts/index.html', banks=banks)

@bank_account_bp.route('/create', methods=['GET', 'POST'])
def create():
    ba_controller.create_bank_account()
    return redirect(url_for('bank_account.index'))