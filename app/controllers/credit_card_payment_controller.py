from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
import traceback

from app.extensions import db
from app.models.credit_card_payment import CreditCardPayment
from app.models.credit_card import CreditCard
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import *

def create_credit_card_payment():
    try:
        amount = Decimal(request.form.get('amount'))
        credit_card_id = request.form.get('credit-card-id') 
        bank_account_id = request.form.get('select-bank-account')

        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        credit_card = CreditCard.query.get(credit_card_id)
        if not credit_card: raise CreditCardDoesNotExists('Credit card record was not found.')
        
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account: raise BankAccountDoesNotExists('You need to select a bank account.')

        credit_card_payment = CreditCardPayment(
            amount=amount,
            bank_account_id=bank_account_id,
            credit_card_id=credit_card_id,
        )

        credit_card.amount_available += amount

        h_update_bank_account_money_on_create(bank_account_id, amount)

        db.session.add(credit_card_payment)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e

def update_credit_card_payment(id):
    try:
        payment = CreditCardPayment.query.get(id)
        if not payment: raise CreditCardPaymentDoesNotExists('This credit card payment was not found.')

        amount = Decimal(request.form.get('amount'))
        bank_account_id = request.form.get('select-bank-account')

        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account: raise BankAccountDoesNotExists('You need to select a bank account.')
        
        h_update_bank_account_money_on_update(
            payment.bank_account_id, 
            bank_account_id,
            payment.amount,
            amount
        )

        h_update_credit_card_amount_available_on_update(
            credit_card=payment.credit_card, 
            old_amount=payment.amount, 
            new_amount=amount
        )

        payment.amount=amount
        payment.bank_account_id=bank_account_id

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

#HELPERS
def h_update_bank_account_money_on_create(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    if bank_account.amount_available <= 0:
        raise NoAvailableMoney('Bank Account does not have any money left.')
    if bank_account.amount_available < amount:
        raise AmountGreaterThanAvailableMoney('Insufficient founds.')
    
    bank_account.amount_available -= amount

def h_update_bank_account_money_on_update(old_ba_id, new_ba_id, old_amount, new_amount):
    if (old_ba_id == new_ba_id) and (old_amount == new_amount): return

    old_bank_account = None
    new_bank_account = None

    try:
        if old_ba_id: #if the bank account id is true it means it's bank account to bank account transaction
            old_bank_account = BankAccount.query.get(old_ba_id)
            if not old_bank_account:
                raise BankAccountDoesNotExists('Bank account does not exists.')   
            old_bank_account.amount_available += old_amount; #refund the money used to the previous bank account
        
        new_bank_account = BankAccount.query.get(new_ba_id)

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
        
def h_update_credit_card_amount_available_on_update(credit_card, old_amount, new_amount):
    credit_card.amount_available -= old_amount
    credit_card.amount_available += new_amount