from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.models.bank_account import BankAccount
from app.models.expense import Expense
from app.models.bank import Bank
from app.models.loan_payment import LoanPayment
from app.utils.numeric_casting import is_decimal_type, total_amount, format_amount
from app.exceptions.bankProductsException import BankAccountDoesNotExists, AmountIsLessThanOrEqualsToZero
from app.extensions import db

def create_bank_account():
    try:
        if request.method == 'POST':
            nick_name = request.form['nick-name']
            amount_available = Decimal(request.form['amount-available']) if is_decimal_type(request.form['amount-available']) else Decimal('0')
            account_number = request.form['account-number']
            bank_id = int(request.form['select-banks'])

            if(amount_available <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce valid number bigger than 0')

            bank_account = BankAccount(
                nick_name=nick_name,
                amount_available=amount_available,
                account_number=account_number,
                bank_id=bank_id
            )

            db.session.add(bank_account)
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def update_bank_account(bank_account):
    try:
        if request.method == 'PUT':
            bank_account.nick_name = request.form['e-nick-name'];
            bank_account.account_number = request.form['e-account-number'];
            bank_account.amount_available = Decimal(request.form['e-amount-available']) if is_decimal_type(request.form['e-amount-available']) else Decimal('0')

            if(bank_account.amount_available <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce valid number bigger than 0')

            bank_id = request.form['e-select-banks'];
            bank_account.bank_id = int(bank_id)

            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def delete_bank_account(bank_account):
    try:        
        db.session.delete(bank_account)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def get_associated_records(bank_account_id):
    try:
        data = {}
        bank_account = BankAccount.query.get(bank_account_id) 
        data = {
            'bank_account': bank_account,
            'total_amount': total_amount, #this the utility function to transfor decimal objects into a readable currency string
            'format_amount': format_amount,
        }
        return data
    except BankAccountDoesNotExists as e:
        raise BankAccountDoesNotExists('Bank account does not exists.')
    except Exception as e:
        raise e