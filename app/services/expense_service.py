"""Business rules for expenses.

Nothing in this file knows about Flask requests or responses: functions take plain arguments and
return model objects (or plain dicts), so the same code can serve any controller, a React
frontend included.

Every function that writes money runs inside atomic(): the expense, the balance of the bank
account / credit card and the ledger rows are saved together with a single commit, or not at all.
"""
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, or_

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.credit_card import CreditCard
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.models.expense import Expense
from app.models.expense_category import ExpenseCategory
from app.exceptions.bankProductsException import NoBankProductSelected
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import get_time_now
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=Expense,
    # outer joins keep expenses that have no bank account, credit card or category
    joins=(Expense.bank_account, Expense.credit_card, Expense.expense_category),
    text_columns=(CreditCard.nick_name, BankAccount.nick_name, ExpenseCategory.name, Expense.description, Expense.amount),
    extra_filter_columns=(Expense.code,),
    keywords=(('yes', 'no', Expense.is_cash),),
)


# ------------------------------------------------------------------ writes

def create_expense(*, amount, is_cash, expense_category_id, description,
                   credit_card_id=None, bank_account_id=None, created_at=None):
    """Record an expense, take the money from the chosen bank product and write the ledgers.

    `created_at` is optional and defaults to the current time.
    """
    amount = money.validate_amount(amount)
    credit_card_id, bank_account_id = _products_for(is_cash, credit_card_id, bank_account_id)

    with atomic():
        if credit_card_id:
            money.take(money.get_credit_card(credit_card_id), amount)
        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)

        expense = Expense(
            amount=amount,
            is_cash=is_cash,
            expense_category_id=expense_category_id,
            credit_card_id=credit_card_id,
            bank_account_id=bank_account_id,
            description=description,
            created_at=created_at or get_time_now(),
        )
        db.session.add(expense)
        db.session.flush()  # gives the expense its id and code, which the ledgers refer to

        if expense.is_cash:
            CashLedger.create(expense, commit=False)
        if expense.bank_account_id:
            BankAccountTransactionsLedger.create(expense, commit=False)
        if expense.credit_card_id:
            CreditCardTransactionsLedger.create(expense, commit=False)

    return expense


def update_expense(expense_id, *, amount, is_cash, expense_category_id, description,
                   credit_card_id=None, bank_account_id=None, created_at=None):
    """Change an expense: give the old amount back to where it came from, take the new amount
    from where it comes from now, and bring the ledgers in line.

    `created_at` is optional; when omitted the expense keeps its date.
    """
    amount = money.validate_amount(amount)
    credit_card_id, bank_account_id = _products_for(is_cash, credit_card_id, bank_account_id)

    with atomic():
        expense = money.get_record(Expense, expense_id, 'Expense')

        _refund(expense)

        if credit_card_id:
            money.take(money.get_credit_card(credit_card_id), amount)
        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)

        expense.amount = amount
        expense.is_cash = is_cash
        expense.expense_category_id = expense_category_id
        expense.credit_card_id = credit_card_id
        expense.bank_account_id = bank_account_id
        expense.description = description
        if created_at:
            expense.created_at = created_at

        db.session.flush()
        # the ledgers read expense.bank_account / expense.credit_card, which now point somewhere else
        db.session.expire(expense, ['bank_account', 'credit_card'])

        CashLedger.update_or_delete(expense, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(expense, commit=False)
        CreditCardTransactionsLedger.update(expense, commit=False)

    return expense


def delete_expense(expense_id):
    """Delete an expense, give its money back and remove its ledger rows."""
    with atomic():
        expense = money.get_record(Expense, expense_id, 'Expense')

        _refund(expense)

        BankAccountTransactionsLedger.delete(expense, commit=False)
        CreditCardTransactionsLedger.delete(expense, commit=False)
        CashLedger.delete(expense, commit=False)

        db.session.delete(expense)


# ------------------------------------------------------------------ reads

def get_monthly_expenses_records():
    """Expenses of the current month, newest first."""
    now = datetime.now()

    return (
        Expense.query
        .filter(
            func.extract('year', Expense.created_at) == now.year,
            func.extract('month', Expense.created_at) == now.month,
        )
        .order_by(Expense.created_at.desc())
        .all()
    )


def get_weekly_expenses_records():
    """Expenses of the current week (Monday to Sunday), newest first."""
    today = datetime.today()
    start_of_week = (today - timedelta(days=today.weekday())).date()
    end_of_week = start_of_week + timedelta(days=7)  # up to the end of Sunday

    return (
        Expense.query
        .filter(Expense.created_at >= start_of_week)
        .filter(Expense.created_at <= end_of_week)
        .order_by(Expense.created_at.desc())
        .all()
    )


def money_limit_spent_left(expenses):
    """How much of the combined category limits the given expenses used."""
    spent = Decimal()
    for expense in expenses:
        spent += expense.amount

    limit = (
        ExpenseCategory.query
        .filter(or_(ExpenseCategory.is_deleted == False, ExpenseCategory.is_deleted.is_(None)))  # noqa: E712
        .with_entities(func.sum(ExpenseCategory.limit))
        .scalar() or Decimal(0.00)
    )

    return {
        'limit': limit,
        'spent': spent,
        'left': Decimal(limit - spent),
    }


def list_between_dates(start_date, end_date):
    """Expenses from `start_date` up to the end of `end_date` (both datetime), newest first."""
    return search_service.between_dates(SPEC, start_date, end_date)


def list_by_is_cash(is_cash):
    return Expense.query.filter(Expense.is_cash == is_cash).all()


def sum_by_is_cash(is_cash):
    return (
        Expense.query
        .filter(Expense.is_cash == is_cash)
        .with_entities(func.sum(Expense.amount))
        .scalar() or Decimal(0.00)
    )


def search(query):
    """Free text search over description, amount, account, card and category (used by the search box)."""
    return search_service.search(SPEC, query)


def filter_expenses(query=None, start=None, end=None):
    """Combined filter: free text and/or a date range (`start` / `end` are 'YYYY-MM-DD' strings).

    Typing exactly "yes" or "no" filters on the cash flag instead of searching text.
    """
    return search_service.filter_all(SPEC, query, start, end)


# ------------------------------------------------------------------ helpers

def _products_for(is_cash, credit_card_id, bank_account_id):
    """A cash expense has no bank product; any other expense needs at least one."""
    if is_cash:
        return None, None

    if not credit_card_id and not bank_account_id:
        raise NoBankProductSelected('You must select either a credit card or bank account.')

    return credit_card_id or None, bank_account_id or None


def _refund(expense):
    """Give an expense's amount back to the bank account / credit card it was taken from."""
    if expense.bank_account:
        money.give(expense.bank_account, expense.amount)
    if expense.credit_card:
        money.give(expense.credit_card, expense.amount)
