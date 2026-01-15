from flask import request, jsonify

import traceback
from datetime import datetime, timedelta

from app.extensions import db
from app.models.debt import Debt
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, NoBankProductSelected
from app.utils.numeric_casting import is_decimal_type

def create():
    try:
        pass
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400