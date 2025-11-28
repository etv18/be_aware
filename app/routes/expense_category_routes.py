from flask import Blueprint, render_template, redirect, url_for, request, jsonify

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

@expense_category_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        expense_category = ExpenseCategory.query.get(id)
        if expense_category:
            ec_controller.delete_expense_category(expense_category)

            return jsonify({'message': 'Expense deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': str(e)}), 400
    return redirect(url_for('income.index'))

@expense_category_bp.route('/associated_records/<int:category_id>')
def show_associated_records(category_id):
    try:
        data = ec_controller.get_associated_records(category_id)
        return render_template('expense_categories/associated_records.html', data=data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@expense_category_bp.route('/monthly/chart')
def populate_monthly_chart():
    try: 
        data = ec_controller.get_monthly_data()
        return jsonify(data), 200
    except Exception as e:
        raise e