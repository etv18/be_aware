from flask import request
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.models.income import Income
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import BankAccountDoesNotExists, AmountIsLessThanOrEqualsToZero
from app.extensions import db

def create_income():
        try:    
            amount = Decimal(request.form['amount'])
            is_cash = request.form.get('is-cash') == 'on'
            bank_account_id = None

            if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

            if not is_cash:
                bank_account_id = int(request.form.get('select-bank-account'))
                update_bank_account_money_on_create(bank_account_id, amount)
                
            income = Income(
                amount=amount,
                is_cash=is_cash,
                bank_account_id=bank_account_id
            )

            db.session.add(income)
            db.session.commit()

        except (AmountIsLessThanOrEqualsToZero, BankAccountDoesNotExists) as e:
            db.session.rollback()
            raise e
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception('Database error occurred: ' + str(e))
        except Exception as e:
            db.session.rollback()
            raise e

def update_income(income):
    try:
        old_amount = income.amount #Get the old amount in case is_cash is False so you can update the bank account's money.
        income.amount = Decimal(request.form['amount'])
        income.is_cash = request.form.get('is-cash') == 'on'
        income.bank_account_id = None
        selected_bank_account = request.form.get('select-bank-account')

        if(income.amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if not income.is_cash and selected_bank_account != None:
            income.bank_account_id = int(selected_bank_account)
            new_amount = income.amount #Get latest amount so you can update the bank account's money accurately
            income.bank_account_id = int(selected_bank_account)
            update_bank_account_money_on_update(income.bank_account_id, old_amount, new_amount)
            
        db.session.commit()

    except (AmountIsLessThanOrEqualsToZero, BankAccountDoesNotExists) as e:
        db.session.rollback()
        raise e
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e

def delete_income(income):
    try:
        db.session.delete(income)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e 

def update_bank_account_money_on_create(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    if amount <= 0:
        raise AmountIsLessThanOrEqualsToZero('You need to enter an amount greater than 0')
    
    bank_account.amount_available += amount

def update_bank_account_money_on_update(id, old_amount, new_amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    
    if new_amount <= 0:
        raise AmountIsLessThanOrEqualsToZero('You need to enter an amount greater than 0')
    
    bank_account.amount_available -= old_amount
    bank_account.amount_available += new_amount