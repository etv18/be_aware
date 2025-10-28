from flask import Blueprint, render_template, redirect, url_for, request

from app.controllers import expense_category_controller as ec_controller
from app.models.expense_category import ExpenseCategory

expense_category_bp = Blueprint('expense_category',__name__, url_prefix='/expense_categories')

@expense_category_bp.route('/index', methods=['GET'])
def index():
    expense_categories = ExpenseCategory.query.all()

    return render_template('expense_categories/index.html', expense_categories=expense_categories)

@expense_category_bp.route('/create', methods=['GET', 'POST'])
def create():
    ec_controller.create_expense_category()

    return redirect(url_for('expense_category.index'))

@expense_category_bp.route('/update', methods=['GET', 'POST'])
def update():
    expense_category_id = request.form['id']
    expense_category = ExpenseCategory.query.get(expense_category_id)
    if expense_category:
        ec_controller.update_expense_category(expense_category)

    return redirect(url_for('expense_category.index'))

@expense_category_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    expense_category = ExpenseCategory.query.get(id)
    if expense_category:
        ec_controller.delete_expense_category(expense_category)

    return redirect(url_for('expense_category.index'))