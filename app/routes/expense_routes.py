from flask import request, redirect, url_for, render_template, Blueprint

from app.models.expense import Expense
from app.controllers import expense_controller
from app.models import credit_card, expense_category, bank_account, expense

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

@expense_bp.route('/index', methods=['GET'])
def index():
    credit_cards = credit_card.CreditCard.query.all()
    expense_categories = expense_category.ExpenseCategory.query.all()
    bank_accounts = bank_account.BankAccount.query.all()
    expenses = expense.Expense.query.all()

    context = {
        'credit_cards': credit_cards,
        'expense_categories': expense_categories,
        'bank_accounts': bank_accounts,
        'expenses':expenses
    }

    return render_template('expenses/index.html', **context)

@expense_bp.route('/create', methods=['GET', 'POST'])
def create():
    expense_controller.create_expense()

    return redirect(url_for('expense.index'))