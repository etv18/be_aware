from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from app.models.cash_ledger import CashLedger
from app.controllers import cashledger_controller

cashlegder_bp = Blueprint('cashledger', __name__, url_prefix='/cashledger')

@cashlegder_bp.route('/index')
def index():
    ledgers = CashLedger.query.order_by(CashLedger.created_at.desc()).all()
    sum_result = CashLedger.query.with_entities(func.sum(CashLedger.amount)).scalar() or 0
    context = {
        'ledgers': ledgers, 
        'sum_result': sum_result,
    }
    return render_template('cashledger/index.html', **context)

@cashlegder_bp.route('/create/adjustment', methods=['POST'])
def create_adjustment():
    try:
       return cashledger_controller.create_adjustment()
    except Exception as e:
        raise e

@cashlegder_bp.route('/filter/cashledger/by/field')
def filter_by_field():
    try:
       query = request.args.get('query') 
       return cashledger_controller.filter_by_field(query)
    except Exception as e:
        raise e
    
@cashlegder_bp.route('/filter/cashledger/by/time')
def filter_by_time():
    try:
       start = request.args.get('start')
       end = request.args.get('end')
       return cashledger_controller.filter_by_time(start, end)
    except Exception as e:
        raise e
    
@cashlegder_bp.route('/filter/all', methods=['POST'])
def filter_all():
    try:
       return cashledger_controller.filter_all()
    except Exception as e:
        raise e