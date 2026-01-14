from flask import Blueprint, jsonify, request, render_template

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.controllers import bank_transaction_ledger_controller as controller

bank_transaction_ledger_bp = Blueprint('bank_transaction_ledger', __name__, url_prefix='/bank_transaction_ledger')

@bank_transaction_ledger_bp.route('/index')
def index():
    render_template('/bank_transaction_ledger/index.html')