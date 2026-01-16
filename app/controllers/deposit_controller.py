from flask import request, jsonify
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
from app.models.deposit import Deposit
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import *
from app.exceptions.generic import *
from app.utils.numeric_casting import is_decimal_type
from app.utils.filter_data import get_total_amount

def create():
    try: 
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')

        description = request.form.get('description')
        bank_account_id = None
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if(amount > get_total_amount(CashLedger)): raise AmountGreaterThanAvailableMoney('You do not have enough cash available for this deposit')
        
        bank_account_id = request.form.get('select-bank-account')
        bank_account = BankAccount.query.get(bank_account_id) 
        if not bank_account: raise NoBankProductSelected('No bank account was selected for this deposit')

        deposit = Deposit(
            amount=amount,
            description=description,
            bank_account_id=bank_account_id,
        )

        _update_bank_account_money_on_create(bank_account, amount)

        db.session.add(deposit)
        db.session.commit()

        CashLedger.create(deposit)
        BankAccountTransactionsLedger.create(deposit)

        return jsonify({'message': 'deposit created successfully'}), 200

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
 
def update(id):
    try: 
        deposit = Deposit.query.get(id)
        if not deposit: raise NotRecordFound('No deposit record was found')

        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        description = request.form.get('description')
        bank_account_id = None
        bank_account_id = request.form.get('select-bank-account')
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if(amount > get_total_amount(CashLedger)): raise AmountGreaterThanAvailableMoney('You do not have enough cash available for this deposit')

        bank_account = BankAccount.query.get(bank_account_id) 
        if not bank_account: raise NoBankProductSelected('No bank account was selected for this deposit')

        _update_bank_account_money_on_update(
            old_bank_account=deposit.bank_account,
            new_bank_account=bank_account,
            old_amount=deposit.amount,
            new_amount=amount
        )

        deposit.amount = amount
        deposit.description = description
        deposit.bank_account_id = bank_account_id
        
        db.session.commit()

        CashLedger.update_or_delete(deposit)
        BankAccountTransactionsLedger.update(deposit)

        return jsonify({'message': 'deposit updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
'''
def delete(id):
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
        raise e
'''
    
def filter_withdrawals_by_field(query):
    try:
        q = f'%{query}%'
        filters = [
            (Deposit.amount.ilike(q)),
            (Deposit.description.ilike(q)),
            (BankAccount.nick_name.ilike(q))
        ]

        deposits = (
            Deposit.query
            .outerjoin(Deposit.bank_account)
            .filter(or_(*filters))
            .order_by(Deposit.created_at.desc())
            .all()
        )

        deposits_list = []
        for deposit in deposits:
            deposits_list.append(deposit.to_dict())

        return deposits_list
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
    
def filter_withdrawals_by_timeframe(start, end):
    try:
        if not start or not end:
            return jsonify({'error': 'Missing data range.'})
        
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        deposits_list = []

        deposits = (
            Deposit.query
            .filter(Deposit.created_at.between(start_date, end_date))
            .order_by(Deposit.created_at.desc())
            .all()
        )

        for deposit in deposits:
            deposits_list.append(deposit.to_dict())

        return deposits_list
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
    

'''HELPERS'''
def _update_bank_account_money_on_create(bank_account, amount):

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    
    bank_account.amount_available += amount


def _update_bank_account_money_on_update(old_bank_account, new_bank_account, old_amount, new_amount):
    if (old_bank_account.id == new_bank_account.id) and (old_amount == new_amount): return

    try:
        if not old_bank_account:  
            raise BankAccountDoesNotExists('Bank account does not exists.')   
        if old_bank_account.amount_available <= 0:
            raise NoAvailableMoney(f"'{old_bank_account.nick_name}' bank account does not have any money left.")
        if old_bank_account.amount_available < new_amount:
            raise AmountGreaterThanAvailableMoney(f"Insufficient founds from '{old_bank_account.nick_name}' bank account.")
        
        old_bank_account.amount_available -= old_amount; #subtract the money used from previous bank account
        
        if not new_bank_account:
            raise BankAccountDoesNotExists('Bank account does not exists.')

        
        new_bank_account.amount_available += new_amount;
    except Exception as e:
        traceback.print_exc()
        raise e