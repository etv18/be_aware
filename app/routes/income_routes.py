from flask import Blueprint, redirect, render_template, request, url_for, jsonify

from app.extensions import db
from app.models import income, bank_account
from app.models.income import Income
from app.models.bank_account import BankAccount
from app.controllers import income_controller

income_bp = Blueprint('income', __name__, url_prefix='/incomes')

@income_bp.route('/index', methods=['GET', 'POST'])
def index():
    incomes = Income.query.all()
    bank_accounts = BankAccount.query.all()

    context = {
        'incomes': incomes,
        'bank_accounts': bank_accounts
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

@income_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    income = Income.query.get(id)
    if income:
        income_controller.delete_income(income)
    return redirect(url_for('income.index'))
