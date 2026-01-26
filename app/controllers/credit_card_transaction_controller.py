from flask import request, jsonify

import traceback
from datetime import datetime, timedelta

from app.extensions import db
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.models.credit_card import CreditCard
from app.utils.numeric_casting import total_amount

def filter_by_field(query):
    try:
        q = f'%{query}%'
        filters = [
            (CreditCardTransactionsLedger.amount.ilike(q)),
            (CreditCardTransactionsLedger.before_update_balance.ilike(q)),
            (CreditCardTransactionsLedger.after_update_balance.ilike(q)),
            (CreditCardTransactionsLedger.reference_code.ilike(q)),
            (CreditCardTransactionsLedger.transaction_type.ilike(q)),
            (CreditCardTransactionsLedger.created_at.ilike(q)),
            (CreditCard.nick_name.ilike(q))
        ]

        ledgers = (
            CreditCardTransactionsLedger.query
            .outerjoin(CreditCardTransactionsLedger.credit_card)
            .filter(db.or_(*filters))
            .order_by(CreditCardTransactionsLedger.created_at.desc())
            .all()
        )

        ledgers_list = []
        for l in ledgers:
            ledgers_list.append(l.to_dict())
        
        return jsonify({
            'ledgers': ledgers_list,
            'total': total_amount(ledgers)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e

def filter_by_time(start, end):
    try:
        if not start or not end:
            return jsonify({'error': 'Missing data range.'})

        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        ledgers = (
            CreditCardTransactionsLedger.query
            .filter(CreditCardTransactionsLedger.created_at.between(start_date, end_date))
            .order_by(CreditCardTransactionsLedger.created_at.desc())
            .all()
        )

        ledgers_list = []
        for l in ledgers:
            ledgers_list.append(l.to_dict())
        
        return jsonify({
            'ledgers': ledgers_list,
            'total': total_amount(ledgers)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
    
   
def filter_all():
    try:
        data = request.get_json(silent=True) or {}

        query = data.get('query')
        start = data.get('start')
        end = data.get('end')

        if not query and (not start or not end):
            return jsonify({
                'error': 'Try to type some query or select a time frame.'
            }), 400

        and_filters = []

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            end_date += timedelta(days=1)
            and_filters.append(CreditCardTransactionsLedger.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'

            text_filters = db.or_(
                (CreditCardTransactionsLedger.amount.ilike(q)),
                (CreditCardTransactionsLedger.before_update_balance.ilike(q)),
                (CreditCardTransactionsLedger.after_update_balance.ilike(q)),
                (CreditCardTransactionsLedger.reference_code.ilike(q)),
                (CreditCardTransactionsLedger.transaction_type.ilike(q)),
                (CreditCardTransactionsLedger.created_at.ilike(q)),
                (CreditCard.nick_name.ilike(q))
            )

            and_filters.append(text_filters)

        ledgers = (
            CreditCardTransactionsLedger.query
            .outerjoin(CreditCardTransactionsLedger.credit_card)
            .filter(db.and_(*and_filters))
            .order_by(CreditCardTransactionsLedger.created_at.desc())
            .all()
        )

        ledgers_list = []
        for l in ledgers:
            ledgers_list.append(l.to_dict())
        
        return jsonify({
            'ledgers': ledgers_list,
            'total': total_amount(ledgers)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500   
