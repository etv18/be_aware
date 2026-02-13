from flask import request, jsonify, current_app as ca
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
from app.models.withdrawal import Withdrawal
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import *
from app.exceptions.generic import *
from app.utils.numeric_casting import is_decimal_type, total_amount

def create_withdrawal():
    try: 
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')

        description = request.form.get('description')
        bank_account_id = None
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        bank_account_id = request.form.get('select-bank-account')
        bank_account = BankAccount.query.get(bank_account_id) 
        if not bank_account: raise NoBankProductSelected('No bank account was selected for this withdrawal')

        withdrawal = Withdrawal(
            amount=amount,
            description=description,
            bank_account_id=bank_account_id,
        )

        h_update_bank_account_money_on_create(bank_account, amount)

        db.session.add(withdrawal)
        db.session.commit()

        CashLedger.create(withdrawal)
        BankAccountTransactionsLedger.create(withdrawal)

    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Unexpected error creating withdrawal")
        raise e
    
def update_withdrawal(id):
    try: 
        withdrawal = Withdrawal.query.get(id)
        if not withdrawal: raise NotRecordFound('No withdrawal record was found')

        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        description = request.form.get('description')
        bank_account_id = None
        bank_account_id = request.form.get('select-bank-account')
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        bank_account = BankAccount.query.get(bank_account_id) 
        if not bank_account: raise NoBankProductSelected('No bank account was selected for this withdrawal')

        h_update_bank_account_money_on_update(
            old_bank_account=withdrawal.bank_account,
            new_bank_account=bank_account,
            old_amount=withdrawal.amount,
            new_amount=amount
        )

        withdrawal.amount = amount
        withdrawal.description = description
        withdrawal.bank_account_id = bank_account_id
        
        db.session.commit()

        CashLedger.update_or_delete(withdrawal)
        BankAccountTransactionsLedger.update(withdrawal)
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error updating withdrawal with id {id}")
        raise e
    
def delete_withdrawal(id):
    try:
        withdrawal = Withdrawal.query.get(id)
        if not withdrawal: raise NotRecordFound('No withdrawal was found')

        withdrawal.bank_account.amount_available += withdrawal.amount #return money used from the selected bank account

        db.session.delete(withdrawal)
        db.session.commit()

        CashLedger.update_or_delete(withdrawal, delete_ledger=True)
        BankAccountTransactionsLedger.delete(withdrawal)
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error deleting withdrawal with id {id}")
        raise e
    
def filter_withdrawals_by_field(query):
    try:
        q = f'%{query}%'
        filters = [
            (Withdrawal.amount.ilike(q)),
            (Withdrawal.description.ilike(q)),
            (BankAccount.nick_name.ilike(q))
        ]

        withdrawals = (
            Withdrawal.query
            .outerjoin(Withdrawal.bank_account)
            .filter(or_(*filters))
            .order_by(Withdrawal.created_at.desc())
            .all()
        )

        withdrawals_list = []
        for w in withdrawals:
            withdrawals_list.append(w.to_dict())

        return jsonify({
            'withdrawals': withdrawals_list,
            'total': total_amount(withdrawals)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error filtering withdrawals by field with query: {query}")
        raise e
    
def filter_all():
    try:
        data = request.get_json(silent=True) or {}

        query = data.get('query')
        start = data.get('start')
        end = data.get('end')

        if not query and (not start or not end):
            ca.logger.error(f"Missing query and/or time frame for filtering withdrawals. Query: {query}, Start: {start}, End: {end}")
            return jsonify({
                'error': 'Try to type some query or select a time frame.'
            }), 400

        and_filters = []

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            end_date += timedelta(days=1)
            and_filters.append(Withdrawal.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'

            text_filters = db.or_(
                (Withdrawal.amount.ilike(q)),
                (Withdrawal.description.ilike(q)),
                (Withdrawal.code.ilike(q)),
                (BankAccount.nick_name.ilike(q))
            )
            and_filters.append(text_filters)

        withdrawals = (
            Withdrawal.query
            .outerjoin(Withdrawal.bank_account)
            .filter(db.and_(*and_filters))
            .order_by(Withdrawal.created_at.desc())
            .all()
        )

        withdrawal_list = []
        for l in withdrawals:
            withdrawal_list.append(l.to_dict())
        
        return jsonify({
            'withdrawals': withdrawal_list,
            'total': total_amount(withdrawals)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error filtering withdrawals with query: {query}, start: {start}, end: {end}")
        return jsonify({'error': 'Internal server error'}), 500   
    
def filter_withdrawals_by_timeframe(start, end):
    try:
        if not start or not end:
            ca.logger.error(f"Missing start and/or end date for filtering withdrawals by timeframe. Start: {start}, End: {end}")
            return jsonify({'error': 'Missing data range.'})
        
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        withdrawals_list = []

        withdrawals = (
            Withdrawal.query
            .filter(Withdrawal.created_at.between(start_date, end_date))
            .order_by(Withdrawal.created_at.desc())
            .all()
        )

        for w in withdrawals:
            withdrawals_list.append(w.to_dict())

        return jsonify({
            'withdrawals': withdrawals_list,
            'total': total_amount(withdrawals)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error filtering withdrawals by timeframe with start: {start} and end: {end}")
        raise e
    

'''HELPERS'''
def h_update_bank_account_money_on_create(bank_account, amount):

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    if bank_account.amount_available <= 0:
        raise NoAvailableMoney('Bank Account does not have any money left.')
    if bank_account.amount_available < amount:
        raise AmountGreaterThanAvailableMoney('Insufficient founds.')
    
    bank_account.amount_available -= amount


def h_update_bank_account_money_on_update(old_bank_account, new_bank_account, old_amount, new_amount):
    if (old_bank_account.id == new_bank_account.id) and (old_amount == new_amount): return

    try:
        if not old_bank_account:  
            raise BankAccountDoesNotExists('Bank account does not exists.')   
        old_bank_account.amount_available += old_amount; #refund the money used to the previous bank account
        
        if not new_bank_account:
            raise BankAccountDoesNotExists('Bank account does not exists.')

        if new_bank_account.amount_available <= 0:
            raise NoAvailableMoney('Bank Account does not have any money left.')
        if new_bank_account.amount_available < new_amount:
            raise AmountGreaterThanAvailableMoney('Insufficient founds.')
        
        new_bank_account.amount_available -= new_amount;
    except Exception as e:
        traceback.print_exc()
        raise e