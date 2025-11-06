from flask import Blueprint, render_template, request, jsonify

from app.controllers import home_controller
home_bp = Blueprint('home', __name__,url_prefix='/home')

@home_bp.route('/index', methods=['GET'])
def index():
    return render_template('home/index.html')

@home_bp.route('/populate_expense_and_income_chart', methods=['GET'])
def populate_expense_and_income_chart():
    data = home_controller.get_income_and_expense_data()
    
    return jsonify(data)


    
