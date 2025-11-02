from flask import Blueprint, redirect, render_template, request, url_for

from app.models import income, bank_account
from app.controllers import income_controller

income_bp = Blueprint('income', __name__, url_prefix='/incomes')

@income_bp.route('/index', methods=['GET', 'POST'])
def index():
    incomes = income.Income.query.all()
    bank_accounts = bank_account.BankAccount.query.all()

    context = {
        'incomes': incomes,
        'bank_accounts': bank_accounts
    }

    return render_template('incomes/index.html', **context)

@income_bp.route('/create', methods=['GET', 'POST'])
def create():
    income_controller.create_income()
    return redirect(url_for('income.index'))

@income_bp.route('/update', methods=['POST'])
def update():
    
    return redirect(url_for('income.index'))
