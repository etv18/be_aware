from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.extensions import db
from app.models.loan import Loan
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.controllers.income_controller import update_bank_account_money_on_create, update_bank_account_money_on_update
from app.models.loan_payment import LoanPayment

def create_loan_payment():
    try:
        amount = Decimal(request.form['amount'])
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

        update_loan_is_active(loan)
        return jsonify({'message': 'Loan payment created successfully'}), 201
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