from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal, ConversionSyntax
from datetime import datetime, timedelta
import traceback

from app.models.income import Income
from app.models.bank_account import BankAccount
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.exceptions.bankProductsException import BankAccountDoesNotExists, AmountIsLessThanOrEqualsToZero, NoBankProductSelected
from app.extensions import db
from app.utils.numeric_casting import is_decimal_type, total_amount, format_amount

def create_income():
        try:
            amount = Decimal(request.form['amount']) if is_decimal_type(request.form['amount']) else Decimal('0')
            is_cash = request.form.get('is-cash') == 'on'
            description = request.form.get('description')
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
                bank_account_id=bank_account_id,
                description=description
            )

            db.session.add(income)
            db.session.commit()

            CashLedger.create(income)
            if income.bank_account_id: BankAccountTransactionsLedger.create(income)

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
        amount = Decimal(request.form['amount']) if is_decimal_type(request.form['amount']) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        description = request.form.get('description')
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
        income.description = description
        income.is_cash = is_cash
        income.bank_account_id = new_bank_account_id

        db.session.commit()

        CashLedger.update_or_delete(income)
        BankAccountTransactionsLedger.update(income)

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
            BankAccountTransactionsLedger.delete(income)
        CashLedger.update_or_delete(income, delete_ledger=True)

        db.session.delete(income)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e 
    

def filter_incomes_by_field(query):
    try:
        q = f'%{query}%'
        filters = [
            (Income.amount.ilike(q)),
            (BankAccount.nick_name.ilike(q)),
            (Income.description.ilike(q))
        ]

        incomes = (
            Income.query
            .outerjoin(Income.bank_account)
            .filter(db.or_(*filters))
            .order_by(Income.created_at.desc())
            .all()
        )
        
        incomes_list = []
        for i in incomes:
            incomes_list.append(i.to_dict())

        return jsonify({
            'incomes': incomes_list,
            'total': total_amount(incomes)
        }), 200


    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
    
def filter_incomes_by_time(start, end):
    try:
        if not start or not end:
            return jsonify({'error': 'Missing data range.'})

        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        incomes = (
            Income.query
            .filter(Income.created_at.between(start_date, end_date))
            .order_by(Income.created_at.desc())
            .all()
        )

        incomes_list = []
        for i in incomes:
            incomes_list.append(i.to_dict())

        return jsonify({
            'incomes': incomes_list,
            'total': total_amount(incomes)
        }), 200

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
    
   
def filter_all():
    try:
        data = request.get_json(silent=True) or {}

        query = data.get('query')
        start = data.get('start')
        end = data.get('end')

        if not query and (not start or not end):
            return jsonify({
                'error': 'Try to type some query or select a time frame.'
            }), 400

        and_filters = []

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            end_date += timedelta(days=1)
            and_filters.append(Income.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'
            
            is_cash = evaluate_boolean_columns(query, 'yes', 'no')    

            if is_cash is not None:
                and_filters.append(Income.is_cash == is_cash)
            else:
                text_filters = db.or_(
                    (Income.amount.ilike(q)),
                    (BankAccount.nick_name.ilike(q)),
                    (Income.description.ilike(q))
                )

                and_filters.append(text_filters)

        incomes = (
            Income.query
            .outerjoin(Income.bank_account)
            .filter(db.and_(*and_filters))
            .order_by(Income.created_at.desc())
            .all()
        )

        income_list = []
        for l in incomes:
            income_list.append(l.to_dict())
        
        return jsonify({
            'incomes': income_list,
            'total': total_amount(incomes)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500   

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

def get_monthly_incomes_records():
    now = datetime.now()
    year = now.year
    month = now.month

    records = (
        Income.query
        .filter(
            db.func.extract('year', Income.created_at) == year,
            db.func.extract('month', Income.created_at) == month
        )
        .order_by(Income.created_at.desc())
        .all()
    )

    return records

def evaluate_boolean_columns(query, reference_for_true, reference_for_false):
    q = query.lower()
    if q == reference_for_true.lower():
        return True
    if q == reference_for_false.lower():
        return False
    return None