from flask import Blueprint, render_template, redirect, url_for, request

from app.controllers import expense_category_controller as ec_controller
from app.models.expense_category import ExpenseCategory

expense_category_bp = Blueprint('expense_category',__name__, url_prefix='/expense_categories')

@expense_category_bp.route('/index', methods=['GET'])
def index():
    return render_template('expense_categories/index.html')