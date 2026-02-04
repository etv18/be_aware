from flask import Blueprint, render_template, request, jsonify

from app.controllers import home_controller
from app.utils.date_handling import get_years

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
def index():
    years = get_years()
    context = {
        'years': years,
    }
    return render_template('home/index.html', **context)

@home_bp.route('/populate/monthly/expense_and_income_chart', methods=['GET'])
def populate_monthly_expense_and_income_chart():
    data = home_controller.get_monthly_income_and_expense_data()
    
    return jsonify(data)

@home_bp.route('/populate/yearly/expense_and_income_chart', methods=['GET'])
def populate_yearly_and_income_chart():
    data = home_controller.get_yearly_income_and_expense_data()
    
    return jsonify(data)


    
