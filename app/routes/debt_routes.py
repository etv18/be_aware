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
    return render_template('accounts_payable/index.html', **context)

@debt_bp.route('/associated/records/<int:id>')
def associated_records(id):
    debt = Debt.query.get(id)
    bank_accounts = BankAccount.query.all()
    context = {
        'debt': debt,
        'bank_accounts': bank_accounts,
        'format_amount': format_amount,
        'total_amount': total_amount,
    }
    return render_template('accounts_payable/associated_records.html', **context)

@debt_bp.route('/create', methods=['POST'])
def create():
    try:
        return controller.create()
    except Exception as e:
        raise e

@debt_bp.route('/update/<int:id>', methods=['PUT'])
def update(id):
    try:
        return controller.update(id)
    except Exception as e:
        raise e

@debt_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return controller.delete(id)
    except Exception as e:
        raise e

@debt_bp.route('/filter/by/field')
def filter_by_field():
    try:
        return controller.filter_by_field()
    except Exception as e:
        raise e

@debt_bp.route('/associated/records/in/json/<int:id>')
def associated_records_in_json(id):
    try:
        return controller.associated_records_in_json(id)
    except Exception as e:
        raise e

@debt_bp.route('/filter/by/time')
def filter_by_time():
    try:
        return controller.filter_by_time()
    except Exception as e:
        raise e
    
