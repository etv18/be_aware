from flask import Blueprint, redirect, render_template, request, url_for, jsonify

from app.controllers import stats_controller as controller

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

@stats_bp.route('/yearly/single/model/report', methods=['POST'])
def yearly_single_model_report():
    try: 
        return controller.yearly_single_model_report()
    except Exception as e:
        raise e

@stats_bp.route('/yearly/all/model/reports', methods=['POST'])
def yearly_all_model_reports():
    try: 
        return controller.yearly_all_model_reports()
    except Exception as e:
        raise e

@stats_bp.route('/yearly/incomes/and/outgoings', methods=['POST'])
def yearly_incomes_and_outgoings():
    try: 
        return controller.yearly_incomes_and_outgoings()
    except Exception as e:
        raise e

@stats_bp.route('/monthly/incomes/and/outgoings', methods=['POST'])
def monthly_incomings_and_outgoings():
    try: 
        return controller.monthly_incomings_and_outgoings()
    except Exception as e:
        raise e

@stats_bp.route('/bank_account/yearly/report/using/source', methods=['POST'])
def bank_account_yearly_report_using_source():
    try: 
        return controller.bank_account_yearly_report_using_source()
    except Exception as e:
        raise e

@stats_bp.route('/credit_card/yearly/report/using/source', methods=['POST'])
def credit_card_yearly_report_using_source():
    try: 
        return controller.credit_card_yearly_report_using_source()
    except Exception as e:
        raise e
    
@stats_bp.route('/cash/yearly/report/using/source', methods=['POST'])
def cash_yearly_report_using_source():
    try: 
        return controller.cash_yearly_report_using_source()
    except Exception as e:
        raise e