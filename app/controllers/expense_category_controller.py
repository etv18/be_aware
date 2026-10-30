"""Expense categories: JSON in, service call, JSON out; plus the expenses of a category and its report."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource, data
from app.models.expense_category import ExpenseCategory
from app.services import expense_category_service

RESOURCE = Resource(
    label='Expense category', model=ExpenseCategory, serialize=ser.expense_category, has_amount=False,
    create_schema=schemas.ExpenseCategoryIn, create=expense_category_service.create_expense_category,
    update=expense_category_service.update_expense_category, delete=expense_category_service.delete_expense_category,
    default_list=expense_category_service.list_visible,
)


def records_of(category_id):
    category = expense_category_service.get_category(category_id)
    expense_category_service.associated_records(category_id)  # 404 for a deleted category
    return data({'expense_category': ser.expense_category(category), 'records': ser.group_by_table(category.expenses)})


def monthly_report():
    return data(expense_category_service.monthly_totals())
