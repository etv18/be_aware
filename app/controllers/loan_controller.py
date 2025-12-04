from flask import request
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.extensions import db
from app.models.loan import Loan
from app.controllers.expense_controller import update_bank_account_money_on_create
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
def create_loan():
    try:
        amount = Decimal(request.form.get('amount'))
        is_cash = request.form.get('is-cash') == 'on'
        person_name = request.form.get('person-name')
        description = request.form.get('description')
        bank_account_id = None
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')
        
        if not is_cash:
            bank_account_id = int(request.form.get('select-bank-account'))
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