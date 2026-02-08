from flask import request, redirect, url_for, render_template, Blueprint, jsonify

from decimal import Decimal

from app.extensions import db
from app.models.expense import Expense
from app.controllers import expense_controller
from app.models import credit_card, expense_category, bank_account, expense
from app.utils.numeric_casting import format_amount, total_amount
from app.utils.date_handling import get_years
from app.utils.filter_data import get_not_deleted_records

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

@expense_bp.route('/index', methods=['GET'])
def index():
    credit_cards = get_not_deleted_records(model=credit_card.CreditCard)
    expense_categories = get_not_deleted_records(model=expense_category.ExpenseCategory)
    bank_accounts = get_not_deleted_records(model=bank_account.BankAccount)
    expenses = expense_controller.get_monthly_expenses_records()
    monthly = expense_controller.money_limit_spent_left_for_expenses(expenses)
    years = get_years()

    context = {
        'credit_cards': credit_cards,
        'expense_categories': expense_categories,
        'bank_accounts': bank_accounts,
        'expenses':expenses,
        'monthly': monthly,
        'format_amount': format_amount, #function
        'total_amount': total_amount, #function
        'years': years,
    }

    return render_template('expenses/index.html', **context)

@expense_bp.route('/create', methods=['GET', 'POST'])
def create():
    try:
        expense_controller.create_expense()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Expense created successfully!'}), 201
            
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print(e)
            return jsonify({'error': str(e)}), 400
        
        raise e

@expense_bp.route('/update/<int:id>', methods=['GET', 'PUT'])
def update(id):
    try:
        expense = Expense.query.get(id)
        if not expense:
            jsonify({'error': 'Expense not found'}), 404
        
        expense_controller.update_expense(expense)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Expense updated successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print(e)
            return jsonify({'error': str(e)}), 400
        raise e

@expense_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        expense = Expense.query.get(id)
        if expense:
            expense_controller.delete_expense(expense)

        return jsonify({'message': 'Expense deleted successfully!'}), 200
    
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': str(e)}), 400

@expense_bp.route('/filter_by_time', methods=['GET'])
def filter_by_time():
    #get start date and end date of expenses you want to see in a certain time frame
    start = request.args.get('start') 
    end = request.args.get('end')

    return expense_controller.filter_by_time(start, end)


@expense_bp.route('/filter_expenses_by_cash/<int:is_cash>', methods=['GET'])
def filter_expenses_by_cash(is_cash):
    try: 
        ic = bool(is_cash) #parse 1 or 0 to True or False
        print(ic)
        return expense_controller.filter_expenses_by_is_cash(ic)
    except Exception as e:
      raise e

@expense_bp.route('/filter_by_field', methods=['GET'])
def filter_by_field():
    try:
        query = request.args.get('query')
        return expense_controller.filter_by_field(query)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@expense_bp.route('/filter/all', methods=['POST'])
def filter_all():
    try:
        return expense_controller.filter_all()
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
