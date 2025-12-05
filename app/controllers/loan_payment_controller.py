from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal

from app.extensions import db
from app.models.loan import Loan
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero

def create_loan_payment():
    try:
        pass
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e
