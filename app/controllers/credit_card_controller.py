from flask import request
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.models.credit_card import CreditCard
from app.extensions import db
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.utils.numeric_casting import is_decimal_type

def create_credit_card():
    try:
        if request.method == 'POST':
            nick_name = request.form['nick-name']
            amount_available = Decimal(request.form['amount-available']) if is_decimal_type(request.form['amount-available']) else Decimal('0')
            limit = Decimal(request.form['limit']) if is_decimal_type(request.form['limit']) else Decimal('0')
            bank_id = request.form['select-banks']

            if(amount_available <= 0 or limit <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')

            credit_card = CreditCard(
                nick_name=nick_name,
                amount_available=amount_available,
                limit=limit,
                bank_id=bank_id
            )

            db.session.add(credit_card)
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def update_credit_card(credit_card):
    try:
        if request.method == 'PUT':
            credit_card.nick_name = request.form['e-nick-name']
            credit_card.limit = Decimal(request.form['e-limit']) if is_decimal_type(request.form['e-limit']) else Decimal('0')
            credit_card.amount_available = Decimal(request.form['e-amount-available']) if is_decimal_type(request.form['e-amount-available']) else Decimal('0')

            if(credit_card.amount_available <= 0 or credit_card.limit <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')


            bank_id = request.form['e-select-banks']
            credit_card.bank_id = int(bank_id)

            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def delete_credit_card(credit_card):
    try:
        db.session.delete(credit_card)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e
    
def h_get_money_used_on_credit_card(cc):
    return cc.limit - cc.amount_available
