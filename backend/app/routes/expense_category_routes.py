from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import expense_category_controller as controller
from app.routes._rest import get, register

expense_category_bp = Blueprint('expense_category', __name__)


@expense_category_bp.get('/expense_categories')
@login_required
def index():
    return render_template('expense_categories.html', nav='categories')


@expense_category_bp.get('/expense_categories/<int:record_id>')
@login_required
def show(record_id):
    return render_template('expense_category.html', nav='categories', id=record_id)


# JSON: GET /api/expense_categories, POST /api/expense_categories, GET /api/expense_categories/<id>, PUT /api/expense_categories/<id>, DELETE /api/expense_categories/<id>
register(expense_category_bp, controller.RESOURCE, '/expense_categories')

# the expenses of one category, and what each category spent this month
get(expense_category_bp, '/expense_categories/<int:category_id>/records', controller.records_of, 'records')
get(expense_category_bp, '/expense_categories/reports/monthly', controller.monthly_report, 'monthly')
