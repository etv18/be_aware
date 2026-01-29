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

def yearly_single_model_report():
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

def yearly_all_model_reports():
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

def yearly_incomes_and_outgoings():
    data = request.get_json(silent=True) or {}
    year = data.get('year')

    incomings = (btc.LoanPayment, btc.Income, btc.Debt)
    outgoings = (btc.Withdrawal, btc.Loan, btc.Expense, btc.CreditCardPayment, btc.DebtPayment)

    incomings_dict = {}
    outgoings_dict = {}

    _dict_info(
        models=incomings,
        container=incomings_dict,
        year=year
    )
    _dict_info(
        models=outgoings,
        container=outgoings_dict,
        year=year
    )

    incoming_list = _total_amount_per_month(incomings_dict)
    outgoing_list = _total_amount_per_month(outgoings_dict)
    
    return jsonify({
        'months': MONTHS,
        'incomings': incoming_list,
        'outgoings': outgoing_list,
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

def _dict_info(models: list, container: dict, year):
    for model in models:
        report = get_yearly_total_amount_info(
            CustomModel=model,
            year=year
        )
        key_name = model.__tablename__
        container[key_name] = report

def _total_amount_per_month(yearly_models_total: dict):
    total_amount_per_month = [Decimal('0.00') for _ in range(12)]

    for yearly in yearly_models_total.values():
        for i in range(0, len(yearly)):
            total_amount_per_month[i] += yearly[i]
    return total_amount_per_month
        

