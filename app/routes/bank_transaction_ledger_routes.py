from flask import Blueprint, jsonify, request, render_template

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.controllers import bank_transaction_ledger_controller as controller
from app.utils.numeric_casting import format_amount

bank_transaction_ledger_bp = Blueprint('bank_transaction_ledger', __name__, url_prefix='/bank_transaction_ledger')

@bank_transaction_ledger_bp.route('/index')
def index():
    ledgers = (
        BankAccountTransactionsLedger.query
        .order_by(BankAccountTransactionsLedger.created_at.desc())
        .all()
    )
    context = {
        'ledgers': ledgers,
        'format_amount': format_amount,
    }
    return render_template('bank_accounts/ledger.html', **context)

@bank_transaction_ledger_bp.route('/filter/by/field')
def filter_by_field():
    try:
        query = request.args.get('query')
        return controller.filter_by_field(query) 
    except Exception as e:
        raise e

@bank_transaction_ledger_bp.route('/filter/by/time')
def filter_by_time():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        return controller.filter_by_time(start, end) 
    except Exception as e:
        raise e
    
