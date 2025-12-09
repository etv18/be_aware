from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

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

        h_update_bank_account_money_on_create(bank_account_id, amount)

        db.session.add(credit_card_payment)
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