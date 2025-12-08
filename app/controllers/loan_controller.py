from flask import request, jsonify
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.extensions import db
from app.models.loan import Loan
from app.models.bank_account import BankAccount
from app.controllers.expense_controller import update_bank_account_money_on_create, update_bank_account_money_on_update
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, NoBankProductSelected

def create_loan():
    try:
        amount = Decimal(request.form.get('amount'))
        is_cash = request.form.get('is-cash') == 'on'
        person_name = request.form.get('person-name')
        description = request.form.get('description')
        bank_account_id = None
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        selected_bank_account_id = request.form.get('select-bank-account')

        if not is_cash:
            if selected_bank_account_id == 'none' or not selected_bank_account_id:
                raise NoBankProductSelected('No bank product was selected for this loan')
            
            bank_account_id = int(selected_bank_account_id)
            update_bank_account_money_on_create(bank_account_id, amount)

        loan = Loan(
            amount=amount,
            is_cash=is_cash,
            person_name=person_name,
            bank_account_id=bank_account_id,
            description=description
        )

        db.session.add(loan)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e
    
def update_loan(loan):
    try:
        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400
        
        amount = Decimal(request.form.get('amount'))
        is_cash = request.form.get('is-cash') == 'on'
        person_name = request.form.get('person-name')
        description = request.form.get('description')
        bank_account_id = None
        if amount <= 0: raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')
        
        selected_bank_account_id = request.form.get('select-bank-account')
        
        if not is_cash:
            if selected_bank_account_id == 'none' or not selected_bank_account_id:
                raise NoBankProductSelected('No bank product was selected for this loan')
            
            bank_account_id = int(selected_bank_account_id)
            update_bank_account_money_on_update(loan.bank_account_id, bank_account_id, loan.amount, amount)
        elif is_cash and loan.bank_account_id:
            return_money_to_bank_account(loan)

        loan.amount = amount
        loan.is_cash = is_cash
        loan.person_name = person_name
        loan.description = description
        loan.bank_account_id = bank_account_id
    
        db.session.commit()

        return jsonify({'data': 'Loan updated successfully'}), 200
    
    except SQLAlchemyError as e:
        print(f'Error on update_loan handler: {e}')
        db.session.rollback()
        raise e
    except Exception as e:
        print(f'Error on update_loan handler: {e}')
        db.session.rollback()
        raise e

def delete_loan(loan):
    try:
        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400
        
        #if the loan is deleted and it was made with a bank account
        #this code will return the money which was used before.
        if loan.bank_account:
            return_money_to_bank_account(loan)
        
        db.session.delete(loan)
        db.session.commit()
        
        return jsonify({'message': 'Loan deleted successfully'}), 200

    except SQLAlchemyError as e:
        print(f'Error on delete_loan handler: {e}')
        db.session.rollback()
        raise e
    except Exception as e:
        print(f'Error on delete_loan handler: {e}')
        db.session.rollback()
        raise e
    
def filter_loans_by_field(query):
    try:
        q = f'%{query}%'
        is_active = evaluate_boolean_columns(query, 'active', 'paid')
        is_cash = evaluate_boolean_columns(query, 'yes', 'no')
        loans_list = []
        filters = [
            (Loan.person_name.ilike(q)),
            (Loan.amount.ilike(q)),
            (Loan.description.ilike(q)),
            (BankAccount.nick_name.ilike(q))
        ]

        if is_active is not None:
            filters.append(Loan.is_active == is_active)

        if is_cash is not None:
            filters.append(Loan.is_cash == is_cash)

        loans = (
            Loan.query
            .join(Loan.bank_account, isouter=True) # allow loans without bank accounts
            .filter(or_(*filters))
            .all()
        )

        for loan in loans:
            loans_list.append(loan.to_dict())

        return jsonify({'loans': loans_list})
    except Exception as e:
        db.session.rollback()
        raise e

#HELPERS
def return_money_to_bank_account(loan):
    loan.bank_account.amount_available += loan.amount

def evaluate_boolean_columns(query, reference_for_true, reference_for_false):
    q = query.lower()
    if q == reference_for_true.lower():
        return True
    if q == reference_for_false.lower():
        return False
    return None


