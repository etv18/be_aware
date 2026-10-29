from flask import Blueprint
from flask_login import login_required

from app.controllers import expense_category_controller as controller
from app.routes._pages import page
from app.routes._rest import register

expense_category_bp = Blueprint('expense_category', __name__, url_prefix='/expense_categories')


@expense_category_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('categories', 'expense-categories', 'Expense categories')


@expense_category_bp.route('/associated_records/<int:category_id>', methods=['GET'])
@login_required
def show_associated_records(category_id):
    return page('categories', 'expense-category', 'Expense category', id=category_id)


register(expense_category_bp, controller.RESOURCE)

expense_category_bp.add_url_rule('/<int:category_id>/records', 'records', login_required(controller.records_of), methods=['GET'])
expense_category_bp.add_url_rule('/reports/monthly', 'monthly', login_required(controller.monthly_report), methods=['GET'])
