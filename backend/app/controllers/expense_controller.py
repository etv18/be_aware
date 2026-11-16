"""Expenses: JSON in, service call, JSON out (see _rest.py for how the five handlers work)."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.controllers.serializers import money
from app.models.expense import Expense
from app.services import expense_service


def _budget(records):
    """What the month's category limits allow, against what these expenses used."""
    figures = expense_service.money_limit_spent_left(records)
    return {'budget': {name: money(value) for name, value in figures.items()}}


RESOURCE = Resource(
    label='Expense', model=Expense, serialize=ser.expense,
    create_schema=schemas.ExpenseIn, create=expense_service.create_expense,
    update=expense_service.update_expense, delete=expense_service.delete_expense,
    default_list=expense_service.get_monthly_expenses_records,
    filter=expense_service.filter_expenses, list_meta=_budget, stored_as_utc=False,
)
