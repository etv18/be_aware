from flask import request, jsonify, current_app as ca

import traceback
from datetime import datetime, timedelta

from app.extensions import db
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import total_amount

def filter_by_field(query):
    try:
        q = f'%{query}%'
        filters = [
            (BankAccountTransactionsLedger.amount.ilike(q)),
            (BankAccountTransactionsLedger.before_update_balance.ilike(q)),
            (BankAccountTransactionsLedger.after_update_balance.ilike(q)),
            (BankAccountTransactionsLedger.reference_code.ilike(q)),
            (BankAccountTransactionsLedger.transaction_type.ilike(q)),
            (BankAccountTransactionsLedger.created_at.ilike(q)),
            (BankAccount.nick_name.ilike(q))
        ]

        ledgers = (
            BankAccountTransactionsLedger.query
            .outerjoin(BankAccountTransactionsLedger.bank_account)
            .filter(db.or_(*filters))
            .order_by(BankAccountTransactionsLedger.created_at.desc())
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
        ca.logger.exception(f"Unexpected error filtering bank transaction ledger by field with query: {query}")
        raise e

def filter_by_time(start, end):
    try:
        if not start or not end:
            ca.logger.error(f"Missing start or end date for filtering bank transaction ledger by time. Start: {start}, End: {end}")
            return jsonify({'error': 'Missing data range.'})

        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        ledgers = (
            BankAccountTransactionsLedger.query
            .filter(BankAccountTransactionsLedger.created_at.between(start_date, end_date))
            .order_by(BankAccountTransactionsLedger.created_at.desc())
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
        ca.logger.exception(f"Unexpected error filtering bank transaction ledger by time with start: {start} and end: {end}")
        raise e
    
def filter_all():
    try:
        data = request.get_json(silent=True) or {}

        query = data.get('query')
        start = data.get('start')
        end = data.get('end')

        if not query and (not start or not end):
            ca.logger.error(f"Missing query and/or start/end date for filtering bank transaction ledger. Query: {query}, Start: {start}, End: {end}")
            return jsonify({
                'error': 'Try to type some query or select a time frame.'
            }), 400

        and_filters = []

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            end_date += timedelta(days=1)
            and_filters.append(BankAccountTransactionsLedger.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'

        #            .outerjoin(Expense.bank_account) #allows to show expense without a bank account


            text_filters = db.or_(
                (BankAccountTransactionsLedger.amount.ilike(q)),
                (BankAccountTransactionsLedger.before_update_balance.ilike(q)),
                (BankAccountTransactionsLedger.after_update_balance.ilike(q)),
                (BankAccountTransactionsLedger.reference_code.ilike(q)),
                (BankAccountTransactionsLedger.transaction_type.ilike(q)),
                (BankAccountTransactionsLedger.created_at.ilike(q)),
                (BankAccount.nick_name.ilike(q))
            )

            and_filters.append(text_filters)

        ledgers = (
            BankAccountTransactionsLedger.query
            .outerjoin(BankAccountTransactionsLedger.bank_account)
            .filter(db.and_(*and_filters))
            .order_by(BankAccountTransactionsLedger.created_at.desc())
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
        ca.logger.exception(f"Unexpected error filtering bank transaction ledger with query: {query}, start: {start}, end: {end}")
        return jsonify({'error': 'Internal server error'}), 500
