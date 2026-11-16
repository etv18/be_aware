from flask import Blueprint

from app.controllers import expense_category_controller as controller
from app.controllers.out import CategoriesMonthlyOut, ExpenseCategoryRecordsOut
from app.routes._rest import get, register

expense_category_bp = Blueprint('expense_category', __name__)


# JSON: GET /api/expense_categories, POST /api/expense_categories, GET /api/expense_categories/<id>, PUT /api/expense_categories/<id>, DELETE /api/expense_categories/<id>
register(expense_category_bp, controller.RESOURCE, '/expense_categories')

# the expenses of one category, and what each category spent this month
get(expense_category_bp, '/expense_categories/<int:category_id>/records', controller.records_of, 'records', out=ExpenseCategoryRecordsOut)
get(expense_category_bp, '/expense_categories/reports/monthly', controller.monthly_report, 'monthly', out=CategoriesMonthlyOut)
