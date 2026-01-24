from flask import Blueprint, redirect, render_template, request, url_for, jsonify

from app.extensions import db
from app.models import income, bank_account
from app.models.income import Income
from app.models.bank_account import BankAccount
from app.controllers import income_controller
from app.utils.numeric_casting import total_amount, format_amount

income_bp = Blueprint('income', __name__, url_prefix='/incomes')

@income_bp.route('/index', methods=['GET', 'POST'])
def index():
    incomes = income_controller.get_monthly_incomes_records()
    bank_accounts = BankAccount.query.all()

    context = {
        'incomes': incomes,
        'bank_accounts': bank_accounts,
        'format_amount': format_amount,
        'total_amount': total_amount,
    }

    return render_template('incomes/index.html', **context)

@income_bp.route('/create', methods=['GET', 'POST'])
def create():
    try:
        income_controller.create_income()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Income created successfully!'}), 201
        
    except Exception as e:
        db.session.rollback()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print(e)
            return jsonify({'error': str(e)}), 400
        
        raise e

@income_bp.route('/update/<int:id>', methods=['PUT'])
def update(id):
    income = Income.query.get(id)
    try:
      
      if not income:
        return jsonify({'error': 'Income record not found'}), 404

      income_controller.update_income(income)

      if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': 'Income edited successfully!'}), 201
      
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print(e)
            return jsonify({'error': str(e)}), 400

@income_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        income = Income.query.get(id)
        if income:
            income_controller.delete_income(income)

        return jsonify({'message': 'Expense deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': str(e)}), 400
    
@income_bp.route('/filter/incomes/by/field', methods=['GET'])
def filter_incomes_by_field():
    try:
        query = request.args.get('query')
        return income_controller.filter_incomes_by_field(query)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@income_bp.route('/filter/incomes/by/time', methods=['GET'])
def filter_incomes_by_time():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        return income_controller.filter_incomes_by_time(start, end)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
