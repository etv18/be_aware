from flask import request, jsonify, redirect, url_for
from sqlalchemy import func, or_

import traceback
from datetime import datetime, timedelta
from decimal import Decimal

from app.extensions import db
from app.models.debt import Debt
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, NoBankProductSelected, AmountGreaterThanAvailableMoney, NoAvailableMoney, BankAccountDoesNotExists
from app.utils.numeric_casting import is_decimal_type
from app.utils.parse_structures import get_data_as_dictionary

def create():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        person_name = request.form.get('person-name')
        description = request.form.get('description')
        bank_account_id = None
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        selected_bank_account_id = request.form.get('select-bank-account')
    

        if not is_cash:
            if selected_bank_account_id == 'none' or not selected_bank_account_id:
                raise NoBankProductSelected('No bank account was selected for this debt')
            
            bank_account_id = int(selected_bank_account_id)
            _add_money_to_back_account(bank_account_id, amount)

        debt = Debt(
            amount=amount,
            is_cash=is_cash,
            person_name=person_name,
            bank_account_id=bank_account_id,
            description=description
        )

        db.session.add(debt)
        db.session.commit()

        CashLedger.create(debt)
        if debt.bank_account_id: BankAccountTransactionsLedger.create(debt)

        return jsonify({'message': 'debt created successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def update(id):
    try:
        debt = Debt.query.get(id)
        if not debt:
            return jsonify({'error': 'Debt record was not found'}), 400
        
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        person_name = request.form.get('person-name')
        description = request.form.get('description')
        bank_account_id = None
        if amount <= 0: raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')
        
        selected_bank_account_id = request.form.get('select-bank-account')


        if not is_cash:
            if selected_bank_account_id == 'none' or not selected_bank_account_id:
                raise NoBankProductSelected('No bank product was selected for this debt')
            
            bank_account_id = int(selected_bank_account_id)
            _update_bank_account_money_on_update(
                old_bank_account=debt.bank_account, 
                new_bank_account_id=bank_account_id, 
                old_amount=debt.amount, 
                new_amount=amount)
        elif debt.bank_account:
            debt.bank_account.amount_available -= debt.amount #subtract the money from the previous bank account if the bank account is changed to other one

        debt.amount = amount
        debt.is_cash = is_cash
        debt.person_name = person_name
        debt.description = description
        debt.bank_account_id = bank_account_id
    
        db.session.commit()

        CashLedger.update_or_delete(debt)
        BankAccountTransactionsLedger.update(debt)
        
        return jsonify({'data': 'Debt updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400 
    
def delete(id):
    try:
        debt = Debt.query.get(id)
        if debt.bank_account:
            _update_bank_account_money_on_delete(debt.bank_account, debt.amount)
            BankAccountTransactionsLedger.delete(debt)
            
        CashLedger.update_or_delete(debt, delete_ledger=True)
        
        _delete_debt_payments_ledgers(debt.debt_payments)

        db.session.delete(debt)
        db.session.commit()

        return jsonify({'data': 'Debt deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def filter_by_field():
    try:
        query = request.args.get('query')
        q = f'%{query}%'

        is_active = _evaluate_boolean_columns(query, 'active', 'paid')
        is_cash = _evaluate_boolean_columns(query, 'yes', 'no')

        debts_list = []

        filters = [
            (Debt.person_name.ilike(q)),
            (Debt.amount.ilike(q)),
            (Debt.description.ilike(q)),
            (Debt.created_at.ilike(q)),
            (BankAccount.nick_name.ilike(q))
        ]

        if is_active is not None:
            filters.append(Debt.is_active == is_active)

        if is_cash is not None:
            filters.append(Debt.is_cash == is_cash)

        debts = (
            Debt.query
            .join(Debt.bank_account, isouter=True) # allow Debts without bank accounts
            .filter(or_(*filters))
            .order_by(Debt.created_at.desc())
            .all()
        )

        for debt in debts:
            debts_list.append(debt.to_dict())

        return jsonify({'debts': debts_list}), 200
    except Exception as e:
        db.session.rollback()
        raise e 
    
def filter_by_time():
    try:
        start = request.args.get('start')
        end = request.args.get('end')

        if not start or not end:
            return jsonify({'error': 'Missing data range.'}), 400
        
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')

        debts_list = []

        debts = (
            Debt.query
            .filter(
                Debt.created_at >= start_date,
                Debt.created_at <= (end_date + timedelta(days=1))
            )
            .order_by(Debt.created_at.desc())
            .all()
        )

        for debt in debts:
            debts_list.append(debt.to_dict())

        return jsonify({'debts': debts_list}), 200
    except Exception as e:
        db.session.rollback()
        raise e

def associated_records_in_json(id):
    try:
        debt = Debt.query.get(id)
        if not debt: 
            return jsonify({'error': 'Debt not found'}), 404

        associations = [
            debt.debt_payments,
        ]
        data = {}
        for a in associations:
            if a:
                table_name = a[0].__class__.__tablename__; '''access the first element to get its table name'''
                data[table_name] = get_data_as_dictionary(a); '''set the table name as the key and use the function to  get all elements of the list in dictionary format'''
        
        return jsonify({'records': data}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

def _add_money_to_back_account(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    
    bank_account.amount_available += amount

def _update_bank_account_money_on_update(old_bank_account, new_bank_account_id, old_amount, new_amount):
    new_bank_account = BankAccount.query.get(new_bank_account_id)

    if not new_bank_account:
        raise BankAccountDoesNotExists('The new bank account does not exists.')
    
    if new_amount <= 0:
        raise AmountIsLessThanOrEqualsToZero('You need to enter an amount greater than 0')
    if old_bank_account:
        old_bank_account.amount_available -= old_amount #Subtract the old amount from the previous bank account
    new_bank_account.amount_available += new_amount

def _update_bank_account_money_on_delete(bank_account, amount):
    if not bank_account:
        raise BankAccountDoesNotExists('The bank account does not exists.')
    
    bank_account.amount_available -= amount

def _delete_debt_payments_ledgers(payments):
    for payment in payments:
        if payment.is_cash:
            CashLedger.delete(payment)
        else:
            payment.bank_account.amount_available += payment.amount
            BankAccountTransactionsLedger.delete(payment)

def _evaluate_boolean_columns(query, reference_for_true, reference_for_false):
    q = query.lower()
    if q == reference_for_true.lower():
        return True
    if q == reference_for_false.lower():
        return False
    return None