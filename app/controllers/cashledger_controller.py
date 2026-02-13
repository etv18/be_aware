from flask import request, jsonify, current_app as ca

import traceback
from datetime import datetime, timedelta
from decimal import Decimal

from app.extensions import db
from app.models.cash_ledger import CashLedger
from app.utils.numeric_casting import total_amount
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.utils.numeric_casting import is_decimal_type
from app.utils.prefixes import ADJUSTMENT
from app.utils.code_generator import generate_montly_sequence

def create_adjustment():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else None
        
        if not amount:
           ca.logger.error(f"Invalid amount for creating cash ledger adjustment: {request.form.get('amount')}")
           return jsonify({'error': 'Introduce a valid number'}), 400

        ref_code = generate_montly_sequence(
            prefix=ADJUSTMENT,
            model=CashLedger,
            field_name='reference_code'
        )

        ledger = CashLedger(
            amount=amount,
            type='ADJUSTMENT',
            reference_code=ref_code
        )

        db.session.add(ledger)
        db.session.commit()

        return jsonify({'message': 'Adjustment created successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Unexpected error creating cash ledger adjustment with amount: {request.form.get('amount')}")
        return jsonify({'error': str(e)}), 500
    
def delete_adjustment(id):
    try:
        adjustment = CashLedger.query.get(id)
        if adjustment:
            if adjustment.type.lower() != 'adjustment': return
            db.session.delete(adjustment)
            db.session.commit()
            return jsonify({'message': 'Adjustment deleted successfully!'}), 200
        return jsonify({'error': 'record not found'}), 404
    except Exception as e:
        db.session.rollback()
        ca.logger.exception(f"Unexpected error deleting cash ledger adjustment with id: {id}")
        return jsonify({'error': str(e)}), 500

def filter_by_field(query):
    try:
        q = f'%{query}%'
        filters = [
            (CashLedger.amount.ilike(q)),
            (CashLedger.reference_code.ilike(q)),
            (CashLedger.type.ilike(q))
        ]

        ledgers = (
            CashLedger.query
            .filter(db.or_(*filters))
            .order_by(CashLedger.created_at.desc())
            .all()
        )

        ledgers_list = []
        for l in ledgers:
            ledgers_list.append(l.to_dict())
        
        return jsonify({
            'ledgers': ledgers_list,
            'total': total_amount(ledgers)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error filtering cash ledger by field with query: {query}")
        raise e
    
def filter_by_time(start, end):
    try:
        if not start or not end:
            ca.logger.error(f"Missing start or end date for filtering cash ledger by time. Start: {start}, End: {end}")
            return jsonify({'error': 'Missing data range.'})

        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        ledgers = (
            CashLedger.query
            .filter(CashLedger.created_at.between(start_date, end_date))
            .order_by(CashLedger.created_at.desc())
            .all()
        )

        ledgers_list = []
        for l in ledgers:
            ledgers_list.append(l.to_dict())
        
        return jsonify({
            'ledgers': ledgers_list,
            'total': total_amount(ledgers)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error filtering cash ledger by time with start: {start} and end: {end}")
        raise e
    
def filter_all():
    try:
        data = request.get_json(silent=True) or {}

        query = data.get('query')
        start = data.get('start')
        end = data.get('end')

        if not query and (not start or not end):
            ca.logger.error(f"Missing query and/or start/end date for filtering cash ledger. Query: {query}, Start: {start}, End: {end}")
            return jsonify({
                'error': 'Try to type some query or select a time frame.'
            }), 400

        and_filters = []

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            end_date += timedelta(days=1)
            and_filters.append(CashLedger.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'

            text_filters = db.or_(
                (CashLedger.amount.ilike(q)),
                (CashLedger.type.ilike(q)),
                (CashLedger.reference_code.ilike(q)),
                (CashLedger.created_at.ilike(q))
            )

            and_filters.append(text_filters)

        ledgers = (
            CashLedger.query
            .filter(db.and_(*and_filters))
            .order_by(CashLedger.created_at.desc())
            .all()
        )

        ledgers_list = []
        for l in ledgers:
            ledgers_list.append(l.to_dict())
        
        return jsonify({
            'ledgers': ledgers_list,
            'total': total_amount(ledgers)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        ca.logger.exception(f"Unexpected error filtering cash ledger with query: {query}, start: {start}, end: {end}")
        return jsonify({'error': 'Internal server error'}), 500   
    
