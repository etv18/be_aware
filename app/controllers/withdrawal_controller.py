from flask import request, jsonify
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.extensions import db
from app.models.withdrawal import Withdrawal
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import *


def create_withdrawal():
    try: 
        amount = Decimal(request.form.get('amount'))
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
    except Exception as e:
        db.session.rollback()
        raise e
    

def h_update_bank_account_money_on_create(bank_account, amount):

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    if bank_account.amount_available <= 0:
        raise NoAvailableMoney('Bank Account does not have any money left.')
    if bank_account.amount_available < amount:
        raise AmountGreaterThanAvailableMoney('Insufficient founds.')
    
    bank_account.amount_available -= amount