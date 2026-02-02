from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from app.controllers import debt_payment_controller as controller
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import format_amount, total_amount
from app.models.debt_payment import DebtPayment

debt_payment_bp = Blueprint('debt_payment', __name__, url_prefix='/debt_payments')

@debt_payment_bp.route('/index')
def index():
    bank_accounts = BankAccount.query.all()
    context = {
        'bank_accounts': bank_accounts,
        'format_amount': format_amount,
        'total_amount': total_amount,
    }
    return render_template('debts/index.html', **context)

@debt_payment_bp.route('/create', methods=['POST'])
def create():
    try:
        return controller.create()
    except Exception as e:
        raise e

@debt_payment_bp.route('/update/<int:id>', methods=['PUT'])
def update(id):
    try:
        return controller.update(id)
    except Exception as e:
        raise e

@debt_payment_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return controller.delete(id)
    except Exception as e:
        raise e

@debt_payment_bp.route('/see/all/debt/payments', methods=['GET'])
def see_all_debt_payments():
    try:
        context = {
            'debt_payments': DebtPayment.query.all(),
            'format_amount': format_amount,
            'total_amount': total_amount,
        }
        return render_template('accounts_payable/debt_payments.html', **context)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400