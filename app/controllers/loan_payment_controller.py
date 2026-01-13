from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.loan import Loan
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.controllers.income_controller import update_bank_account_money_on_create, update_bank_account_money_on_update, update_bank_account_money_on_delete
from app.models.loan_payment import LoanPayment
from app.utils.numeric_casting import is_decimal_type

def create_loan_payment():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        bank_account_id = None
        loan_id = int(request.form['loan-id'])

        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400

        if loan.total_payments() >= loan.amount:
            return jsonify({
                'message': 'Loan is already fully paid',
                'is_paid': True
            }), 200
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if not is_cash:
            bank_account_id = int(request.form.get('select-bank-account'))
            update_bank_account_money_on_create(bank_account_id, amount)

        loan_payment = LoanPayment(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id,
            loan_id=loan_id
        )
        db.session.add(loan_payment)
        db.session.commit()
        
        CashLedger.create(loan_payment)
        if loan_payment.bank_account_id: BankAccountTransactionsLedger.create(loan_payment)

        update_loan_is_active(loan)

        return jsonify({'message': 'Loan payment created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e


def update_loan_payment(loan_payment):
    try:
        if not loan_payment:
            return jsonify({'error': 'Loan payment record was not found'}), 400
        
        new_amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
 
        new_bank_account_id = None
        is_cash = request.form.get('is-cash') == 'on'
        selected_bank_account = request.form.get('select-bank-account')
        loan_id = int(request.form['loan-id'])
        
        
        if(new_amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400

        expected_total_payments = (loan.total_payments() - loan_payment.amount) + new_amount
        if expected_total_payments > loan.amount:
            return jsonify({
                'message': 'The updated amount exceeds the remaining loan balance',
                'is_paid': True
            }), 200
        
        if not is_cash and (selected_bank_account != None or selected_bank_account != '' or selected_bank_account != 'none'):
            new_bank_account_id = int(request.form.get('select-bank-account'))
            new_bank_account = BankAccount.query.get(new_bank_account_id)
            update_bank_account_money_on_update(loan_payment.bank_account, new_bank_account, loan_payment.amount, new_amount)

        loan_payment.amount = new_amount
        loan_payment.is_cash = is_cash
        loan_payment.bank_account_id = new_bank_account_id

        db.session.commit()

        CashLedger.update_or_delete(loan_payment)
        BankAccountTransactionsLedger.update(loan_payment)
        
        update_loan_is_active(loan)
        return jsonify({'message': 'Loan payment created successfully'}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e
    
def delete_loan_payment(loan_payment):
    try:
        if not loan_payment:
            return jsonify({'error': 'Loan payment record was not found'}), 400
        
        loan = loan_payment.loan
        if loan_payment.bank_account:
            update_bank_account_money_on_delete(loan_payment.bank_account, loan_payment.amount)

        CashLedger.update_or_delete(loan_payment, delete_ledger=True)

        db.session.delete(loan_payment)
        db.session.commit()

        update_loan_is_active(loan)

        return jsonify({'message': 'Loan payment deleted successfully'}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def update_loan_is_active(loan):
    db.session.refresh(loan)  # <-- refresh from DB
    loan.is_active = loan.remaining_amount() > 0
    db.session.commit()