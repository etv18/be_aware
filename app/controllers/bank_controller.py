from flask import request, current_app as ca

from sqlalchemy.exc import SQLAlchemyError

from app.models.bank import Bank
from app.extensions import db

def create_bank():
    if request.method == 'POST':
        name = request.form['name']

        bank = Bank(name=name)

        db.session.add(bank)
        db.session.commit()
    
def update_bank(bank):
    if request.method == 'POST':
        bank.name = request.form['name']

        db.session.commit()

def delete_bank(bank):
    try:
        db.session.delete(bank)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        ca.logger.exception(f"Database error deleting bank with id {bank.id}")
        raise e
    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Unexpected error deleting bank with id {bank.id}")
        raise e
    