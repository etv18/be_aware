from flask import request, redirect, url_for, render_template, Blueprint, jsonify

from decimal import Decimal

from app.extensions import db
from app.models.expense import Expense
from app.controllers import expense_controller
from app.models import credit_card, expense_category, bank_account, expense

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

@expense_bp.route('/index', methods=['GET'])
def index():
    credit_cards = credit_card.CreditCard.query.all()
    expense_categories = expense_category.ExpenseCategory.query.all()
    bank_accounts = bank_account.BankAccount.query.all()
    expenses = expense_controller.weekly_basis_expenses_info()
    weekly = expense_controller.money_limit_spent_left_for_expenses(expenses)

    context = {
        'credit_cards': credit_cards,
        'expense_categories': expense_categories,
        'bank_accounts': bank_accounts,
        'expenses':expenses,
        'weekly': weekly,
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

@expense_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    expense = Expense.query.get(id)
    if expense:
        expense_controller.delete_expense(expense)
    return redirect(url_for('expense.index'))

@expense_bp.route('/filter_by_time', methods=['GET'])
def filter_by_time():
    #get start date and end date of expenses you want to see in a certain time frame
    start = request.args.get('start') 
    end = request.args.get('end')

    data = expense_controller.filter_by_time(start, end)
    return jsonify(data)

