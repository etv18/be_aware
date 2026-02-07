from flask import request, jsonify
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
import app.utils.bank_transactional_classes as btc
import app.utils.cash_transactional_classes as ctc
from app.utils.filter_data import get_yearly_total_amount_info, get_monthly_total_amount_info, get_yearly_total_amount_info_using_source
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
                'months': MONTHS,
                key_name : report,
                'label': key_name.replace('_', ' ').title()
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

    incoming_list = _total_amount_per_month_through_the_year(incomings_dict)
    outgoing_list = _total_amount_per_month_through_the_year(outgoings_dict)
    
    return jsonify({
        'months': MONTHS,
        'incomings': incoming_list,
        'outgoings': outgoing_list,
    }), 200

def monthly_incomings_and_outgoings():
    incomings = (btc.LoanPayment, btc.Income, btc.Debt)
    outgoings = (btc.Withdrawal, btc.Loan, btc.Expense, btc.CreditCardPayment, btc.DebtPayment)

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    incomings_monthly_total = _total_monthly(
        models=incomings,
        year=current_year,
        month=current_month
    )
    outgoings_monthly_total = _total_monthly(
        models=outgoings,
        year=current_year,
        month=current_month 
    )

    return jsonify({
        'incomings': incomings_monthly_total,
        'outgoings': outgoings_monthly_total,
    }), 200

def bank_account_yearly_report_using_source():
    data = request.get_json(silent=True) or {}
    year = data.get('year')
   
    source = 'bank'
    models = btc.get_all()
    reports = {}

    for model in models:
        if model is not btc.BankTransfer: #Only execute when model is not BankTransfer Class
            report = get_yearly_total_amount_info_using_source(
                CustomModel=model,
                year=year,
                source=source
            )
            key_name = model.__tablename__
            reports[key_name] = report

    model = _get_model('bank_transfers')
    report = get_yearly_total_amount_info(
        CustomModel=model,
        year=year,
    )
    key_name = model.__tablename__
    reports[key_name] = report
        
    return jsonify({
        'months': MONTHS,
        'report': reports,
    }), 200

def credit_card_yearly_report_using_source():
    data = request.get_json(silent=True) or {}
    year = data.get('year')
   
    source = 'card'
    models = (btc.CreditCardPayment, btc.Expense)
    reports = {}

    for model in models:
        report = get_yearly_total_amount_info_using_source(
            CustomModel=model,
            year=year,
            source=source
        )
        key_name = model.__tablename__
        reports[key_name] = report
        
    return jsonify({
        'months': MONTHS,
        'report': reports,
    }), 200

def cash_yearly_report_using_source():
    data = request.get_json(silent=True) or {}
    year = data.get('year')
   
    source = 'cash'
    models = (ctc.Loan, ctc.LoanPayment, ctc.Income, ctc.Expense, ctc.Debt, ctc.DebtPayment)
    reports = {}

    for model in models:
        report = get_yearly_total_amount_info_using_source(
            CustomModel=model,
            year=year,
            source=source
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
    elif model_str == 'loan_payment'         : return btc.LoanPayment
    elif model_str == 'credit_card_payments' : return btc.CreditCardPayment
    elif model_str == 'debts'                : return btc.Debt
    elif model_str == 'debt_payments'        : return btc.DebtPayment
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

def _total_amount_per_month_through_the_year(yearly_models_total: dict) -> list:
    total_amount_per_month = [Decimal('0.00') for _ in range(12)]

    for yearly in yearly_models_total.values():
        for i in range(0, len(yearly)):
            total_amount_per_month[i] += yearly[i]
    return total_amount_per_month

def _total_monthly(models, year, month) -> Decimal:
    total = Decimal('0')
    for model in models:
        total += get_monthly_total_amount_info(
            CustomModel=model,
            year=year,
            month=month
        )
    return total
        

