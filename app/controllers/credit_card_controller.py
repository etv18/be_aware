from flask import request, jsonify, current_app as ca
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
import traceback

from app.models.credit_card import CreditCard
from app.extensions import db
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.utils.numeric_casting import is_decimal_type
from app.utils.parse_structures import get_data_as_dictionary
from app.utils.bank_accounts.filter_data import get_yearly_total_amount_info_by_filter_through_custom_model_and_fk
from app.utils.bank_transactional_classes import Expense, CreditCardPayment

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
        ca.logger.exception(f"Database error creating credit card with nick_name")
        raise e
    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Database error creating credit card with nick_name")
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
        ca.logger.exception(f"Database error updating credit card with id {credit_card.id}")
        raise e
    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Unexpected error updating credit card with id {credit_card.id}")
        raise e

def delete_credit_card(credit_card):
    try:
        if credit_card:
            credit_card.is_deleted = True
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        ca.logger.exception(f"Database error deleting credit card with id {credit_card.id}")
        raise e
    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Unexpected error deleting credit card with id {credit_card.id}")
        raise e

def associated_records_in_json(id):
    try:
        credit_card = CreditCard.query.get(id)
        if not credit_card:
            ca.logger.error(f"Credit card with id {id} not found for getting associated records in json")
            return jsonify({'error': 'Credit card not found'}), 404

        associations = [
            credit_card.expenses,
            credit_card.payments,
        ]
        data = {}
        for a in associations:
            if a:
                table_name = a[0].__class__.__tablename__; '''access the first element to get its table name'''
                data[table_name] = get_data_as_dictionary(a); '''set the table name as the key and use the function to  get all elements of the list in dictionary format'''
        
        return jsonify({'records': data}), 200
    except Exception as e:
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error getting associated records in json for credit card with id {id}")
        return jsonify({'error': str(e)}), 400

def get_yearly_total_per_association_info(): 
    data = request.get_json(silent=True) or {}

    credit_card_id = data.get('credit_card_id')
    year = data.get('year')

    associations_info = {}

    for association in (Expense, CreditCardPayment):
        table_name = association.__tablename__
        yearly_info = get_yearly_total_amount_info_by_filter_through_custom_model_and_fk(
            id=credit_card_id,
            CustomModel=association,
            fk_column_name='credit_card_id',
            year=year
        )
        associations_info[table_name] = yearly_info

    data = {
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'associations_info': associations_info,
    }
    return jsonify(data), 200


def h_get_money_used_on_credit_card(cc):
    return cc.limit - cc.amount_available
