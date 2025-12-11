from flask import request
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal, ConversionSyntax

from app.models.income import Income
from app.models.bank_account import BankAccount
from app.models.cash_ledger import CashLedger
from app.exceptions.bankProductsException import BankAccountDoesNotExists, AmountIsLessThanOrEqualsToZero, NoBankProductSelected
from app.extensions import db
from app.utils.is_numeric_type import is_numeric_type

def create_income():
        try:
            amount = Decimal(request.form['amount']) if is_numeric_type(request.form['amount']) else Decimal('0')
            is_cash = request.form.get('is-cash') == 'on'
            bank_account_id = None

            if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

            if not is_cash:
                bank_account_id = int(request.form.get('select-bank-account'))
                if not bank_account_id or bank_account_id == 'none':
                    return NoBankProductSelected('You must select a bank account')
                update_bank_account_money_on_create(bank_account_id, amount)
                
            income = Income(
                amount=amount,
                is_cash=is_cash,
                bank_account_id=bank_account_id
            )

            db.session.add(income)
            db.session.commit()

            CashLedger.create(income)

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
        amount = Decimal(request.form['amount']) if is_numeric_type(request.form['amount']) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        new_bank_account_id = None
        selected_bank_account = request.form.get('select-bank-account')
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if not is_cash:
            if not selected_bank_account or selected_bank_account == 'none': raise NoBankProductSelected('You must select a bank account')
            new_bank_account_id = int(selected_bank_account)
            new_bank_account = BankAccount.query.get(new_bank_account_id)
            if not new_bank_account: raise NoBankProductSelected('You must select a bank account')
            update_bank_account_money_on_update(income.bank_account, new_bank_account, income.amount, amount)
        elif income.bank_account:
            income.bank_account.amount_available -= income.amount

        income.amount = amount
        income.is_cash = is_cash
        income.bank_account_id = new_bank_account_id

        db.session.commit()

        CashLedger.update_or_delete(income)

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
        if income.bank_account:
            update_bank_account_money_on_delete(income.bank_account, income.amount)

        CashLedger.update_or_delete(income, delete_ledger=True)

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

def update_bank_account_money_on_update(old_bank_account, new_bank_account, old_amount, new_amount):

    if not new_bank_account:
        raise BankAccountDoesNotExists('The new bank account does not exists.')
    
    if new_amount <= 0:
        raise AmountIsLessThanOrEqualsToZero('You need to enter an amount greater than 0')
    if old_bank_account:
        old_bank_account.amount_available -= old_amount #Subtract the old amount from the previous bank account
    new_bank_account.amount_available += new_amount

def update_bank_account_money_on_delete(bank_account, amount):
    if not bank_account:
        raise BankAccountDoesNotExists('The bank account does not exists.')
    
    bank_account.amount_available -= amount