from flask import Blueprint, jsonify, request, render_template

from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.controllers import credit_card_transaction_controller as controller
from app.utils.numeric_casting import format_amount, total_amount

credit_card_ledger_bp = Blueprint('credit_card_ledger', __name__, url_prefix='/credit_card_ledger')

@credit_card_ledger_bp.route('/ledger')
def index():
    ledgers = (
        CreditCardTransactionsLedger.query
        .order_by(CreditCardTransactionsLedger.created_at.desc())
        .all()
    )
    context = {
        'ledgers': ledgers,
        'format_amount': format_amount,
        'total_amount': total_amount,
    }
    return render_template('credit_cards/ledger.html', **context)

@credit_card_ledger_bp.route('/filter/by/field')
def filter_by_field():
    try:
        query = request.args.get('query')
        return controller.filter_by_field(query) 
    except Exception as e:
        raise e

@credit_card_ledger_bp.route('/filter/by/time')
def filter_by_time():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        return controller.filter_by_time(start, end) 
    except Exception as e:
        raise e
    
