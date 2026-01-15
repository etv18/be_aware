from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from app.controllers import debt_controller as controller
from app.models.debt import Debt
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import format_amount, total_amount

debt_bp = Blueprint('debt', __name__, url_prefix='/debts')

@debt_bp.route('/index')
def index():
    debts = Debt.query.order_by(Debt.created_at.desc()).all()
    bank_accounts = BankAccount.query.all()
    context = {
        'debts': debts,
        'bank_accounts': bank_accounts,
        'format_amount': format_amount,
        'total_amount': total_amount,
    }
    return render_template('debts/index.html', **context)

@debt_bp.route('/create', methods=['POST'])
def create():
    try:
        return controller.create()
    except Exception as e:
        raise e