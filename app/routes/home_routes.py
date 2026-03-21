from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, logout_user, login_required

from app.controllers import home_controller
from app.models.debt import Debt
from app.models.loan import Loan
from app.utils.date_handling import get_years

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
@login_required
def index():
    years = get_years()
    active_loans = Loan.query.filter(Loan.is_active == True).count()
    active_debts = Debt.query.filter(Debt.is_active == True).count()

    context = {
        'years': years,
        'active_loans': active_loans,
        'active_debts': active_debts,
    }
    return render_template('home/index.html', **context)

@home_bp.route('/populate/monthly/expense_and_income_chart', methods=['GET'])
@login_required
def populate_monthly_expense_and_income_chart():
    data = home_controller.get_monthly_income_and_expense_data()
    
    return jsonify(data)

@home_bp.route('/populate/yearly/expense_and_income_chart', methods=['GET'])
@login_required
def populate_yearly_and_income_chart():
    data = home_controller.get_yearly_income_and_expense_data()
    
    return jsonify(data) 


    
