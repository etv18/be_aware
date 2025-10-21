from flask import Blueprint, render_template, redirect, url_for, request

from app.controllers import bank_account_controller as ba_controller
from app.models.bank_account import BankAccount
from app.models.bank import Bank

bank_account_bp = Blueprint('bank_account', __name__, url_prefix='/bank_accounts')

@bank_account_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.query.all()
    bank_accounts = BankAccount.query.all()

    context = {
        'banks': banks,
        'bank_accounts': bank_accounts
    }

    return render_template('bank_accounts/index.html', **context)

@bank_account_bp.route('/create', methods=['GET', 'POST'])
def create():
    ba_controller.create_bank_account()
    return redirect(url_for('bank_account.index'))

@bank_account_bp.route('/update', methods=['GET', 'POST'])
def update():
    bank_account_id = request.form['id']
    bank_account = BankAccount.query.get(int(bank_account_id))
    if bank_account:
        ba_controller.update_bank_account(bank_account)
    return redirect(url_for('bank_account.index'))

@bank_account_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    bank_account = BankAccount.query.get(id)
    if bank_account:
        ba_controller.delete_bank_account(bank_account)

    return redirect(url_for('bank_account.index'))