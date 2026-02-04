from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from app.controllers import deposit_controller as controller
from app.models.deposit import Deposit
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import format_amount, total_amount
from app.utils.date_handling import get_years

deposit_bp = Blueprint('deposit', __name__, url_prefix='/deposits')

@deposit_bp.route('/index')
def index():
    deposits = Deposit.query.order_by(Deposit.created_at.desc()).all()
    bank_accounts = BankAccount.query.all()
    years = get_years()
    context = {
        'deposits': deposits,
        'bank_accounts': bank_accounts,
        'format_amount': format_amount,
        'total_amount': total_amount,
        'years': years,
    }
    return render_template('deposits/index.html', **context)

@deposit_bp.route('/create', methods=['POST'])
def create():
    try:
        return controller.create()
    except Exception as e:
        raise e

@deposit_bp.route('/update/<int:id>', methods=['PUT'])
def update(id):
    try:
        return controller.update(id)
    except Exception as e:
        raise e

@deposit_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        return controller.delete(id)
    except Exception as e:
        raise e
    
@deposit_bp.route('/filter/by/field')
def filter_by_field():
    try:
        return controller.filter_by_field()
    except Exception as e:
        raise e

@deposit_bp.route('/filter/by/time')
def filter_by_time():
    try:
        return controller.filter_by_time()
    except Exception as e:
        raise e
    
@deposit_bp.route('/filter/all', methods=['POST'])
def filter_all():
    try:
        return controller.filter_all()
    except Exception as e:
        raise e