"""Business rules for expense categories."""
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import extract, func

from app.extensions import db
from app.models.expense import Expense
from app.models.expense_category import ExpenseCategory
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.exceptions.records import RecordNotFound
from app.services import associations, money
from app.utils.transactions import atomic

MIN_NAME_LENGTH = 4


def create_expense_category(*, name, limit):
    name = _validate_name(name)
    limit = _validate_limit(limit)

    with atomic():
        category = ExpenseCategory(name=name, limit=limit)
        db.session.add(category)

    return category


def update_expense_category(category_id, *, name, limit):
    name = _validate_name(name)
    limit = _validate_limit(limit)

    with atomic():
        category = money.get_record(ExpenseCategory, category_id, 'Expense category')
        category.name = name
        category.limit = limit

    return category


def delete_expense_category(category_id):
    """Categories are hidden, not removed, so the expenses filed under them keep their category."""
    with atomic():
        money.get_record(ExpenseCategory, category_id, 'Expense category').is_deleted = True


def list_visible():
    return ExpenseCategory.query.filter_by(is_deleted=False).order_by(ExpenseCategory.name).all()


def get_category(category_id):
    return money.get_record(ExpenseCategory, category_id, 'Expense category')


def associated_records(category_id):
    category = get_category(category_id)
    if category.is_deleted:
        raise RecordNotFound('Expense category not found')

    return associations.group_by_table(category.expenses)


def monthly_totals():
    """{'names': [...], 'totals': [...]}: what each visible category spent this month."""
    now = datetime.now()

    spent_by_category = dict(
        db.session.query(Expense.expense_category_id, func.sum(Expense.amount))
        .filter(extract('year', Expense.created_at) == now.year, extract('month', Expense.created_at) == now.month)
        .group_by(Expense.expense_category_id)
        .all()
    )
    categories = ExpenseCategory.query.filter_by(is_deleted=False).all()

    return {
        'names': [category.name.title() for category in categories],
        'totals': [spent_by_category.get(category.id) or Decimal('0.00') for category in categories],
    }


def _validate_name(name):
    name = (name or '').strip()
    if len(name) < MIN_NAME_LENGTH:
        raise ValueError(f'Category name must have {MIN_NAME_LENGTH} characters or more')
    return name.upper()


def _validate_limit(limit):
    """The limit may be zero (no limit) but not negative."""
    try:
        limit = Decimal(limit)
    except (InvalidOperation, TypeError, ValueError):
        raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')

    if not limit.is_finite() or limit < 0:
        raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')

    return limit.quantize(money.CENTS)
