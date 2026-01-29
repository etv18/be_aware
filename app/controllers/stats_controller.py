from flask import request, jsonify
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
import app.utils.bank_transactional_classes as btc
from app.utils.filter_data import get_yearly_total_amount_info
from app.utils.date_handling import MONTHS

def single_model_report():
    try: 
        data = request.get_json(silent=True) or {}
        model_str = data.get('model')
        year = data.get('year')

        model = _get_model(model_str=model_str)

        if model:
            report = get_yearly_total_amount_info(
                CustomModel=model,
                year=year
            )
            key_name = model.__tablename__
            return jsonify({
               key_name : report,
            })
        
        return jsonify({}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    

def all_model_reports():
    data = request.get_json(silent=True) or {}
    year = data.get('year')

    models = btc.get_all()
    reports = {}

    for model in models:
        report = get_yearly_total_amount_info(
            CustomModel=model,
            year=year
        )
        key_name = model.__tablename__
        reports[key_name] = report
    
    return jsonify({
        'months': MONTHS,
        'report': reports,
    }), 200
    
def _get_model(model_str: str):
    if   model_str == 'expenses'             : return btc.Expense
    elif model_str == 'deposits'             : return btc.Deposit 
    elif model_str == 'withdrawals'          : return btc.Withdrawal
    elif model_str == 'incomes'              : return btc.Income
    elif model_str == 'loans'                : return btc.Loan
    elif model_str == 'loans_payments'       : return btc.LoanPayment
    elif model_str == 'credit_card_payments' : return btc.CreditCardPayment
    elif model_str == 'debts'                : return btc.Debt
    elif model_str == 'debts_payments'       : return btc.DebtPayment
    elif model_str == 'bank_transfers'       : return btc.BankTransfer
    else : return None

