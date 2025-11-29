from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.models.bank_account import BankAccount
from app.models.expense import Expense
from app.models.bank import Bank
from app.exceptions.bankProductsException import BankAccountDoesNotExists, AmountIsLessThanOrEqualsToZero
from app.extensions import db

def create_bank_account():
    try:
        if request.method == 'POST':
            nick_name = request.form['nick-name']
            amount_available = float(request.form['amount-available']) or 0
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
            bank_account.amount_available = float(request.form['e-amount-available']) or 0;

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
    data = {}
    try:
        bank_account = BankAccount.query.get(bank_account_id) 

        query = Expense.query.filter(Expense.bank_account_id == bank_account_id)
        expenses = query.order_by(Expense.created_at.desc()).all()
        count_expenses = query.count()
        total_expenses = query.with_entities(func.sum(Expense.amount)).scalar() or Decimal(0.00)

        data = {
            'expenses': expenses,
            'bank_account': bank_account,
            'total_expenses': total_expenses,
            'count_expenses': count_expenses,
        }
    except BankAccountDoesNotExists as e:
        raise BankAccountDoesNotExists('Bank account does not exists.')
    except Exception as e:
        raise e
    return data