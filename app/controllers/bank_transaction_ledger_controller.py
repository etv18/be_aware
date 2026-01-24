from flask import request, jsonify

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
        raise e

def filter_by_time(start, end):
    try:
        if not start or not end:
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
        raise e