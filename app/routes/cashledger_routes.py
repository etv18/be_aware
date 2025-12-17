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