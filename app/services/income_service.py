"""Business rules for incomes (money coming in, as cash or into a bank account).

No Flask in here. Each write runs in atomic(): the income, the bank balance and the ledger rows
are saved with one commit, or not at all.
"""
from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.income import Income
from app.exceptions.bankProductsException import NoBankProductSelected
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import get_time_now
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=Income,
    joins=(Income.bank_account,),
    text_columns=(Income.amount, BankAccount.nick_name, Income.description),
    extra_filter_columns=(Income.code,),
    keywords=(('yes', 'no', Income.is_cash),),
)


def create_income(*, amount, is_cash, bank_account_id=None, description=None, created_at=None):
    amount = money.validate_amount(amount)
    bank_account_id = _account_for(is_cash, bank_account_id)

    with atomic():
        if bank_account_id:
            money.give(money.get_bank_account(bank_account_id), amount)

        income = Income(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id,
            description=description,
            created_at=created_at or get_time_now(),
        )
        db.session.add(income)
        db.session.flush()  # gives the income its id and code, which the ledgers refer to

        if income.is_cash:
            CashLedger.create(income, commit=False)
        if income.bank_account_id:
            BankAccountTransactionsLedger.create(income, commit=False)

    return income


def update_income(income_id, *, amount, is_cash, bank_account_id=None, description=None, created_at=None):
    amount = money.validate_amount(amount)
    bank_account_id = _account_for(is_cash, bank_account_id)

    with atomic():
        income = money.get_record(Income, income_id, 'Income')

        if income.bank_account:
            income.bank_account.amount_available -= income.amount  # take the old income back out
        if bank_account_id:
            money.give(money.get_bank_account(bank_account_id), amount)

        income.amount = amount
        income.description = description
        income.is_cash = is_cash
        income.bank_account_id = bank_account_id
        if created_at:
            income.created_at = created_at

        db.session.flush()
        db.session.expire(income, ['bank_account'])  # the ledger reads it, and it may point somewhere else now

        CashLedger.update_or_delete(income, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(income, commit=False)

    return income


def delete_income(income_id):
    with atomic():
        income = money.get_record(Income, income_id, 'Income')

        if income.bank_account:
            income.bank_account.amount_available -= income.amount

        BankAccountTransactionsLedger.delete(income, commit=False)
        CashLedger.delete(income, commit=False)
        db.session.delete(income)


# ------------------------------------------------------------------ reads

def get_monthly_incomes_records():
    """Incomes of the current month, newest first."""
    now = datetime.now()

    return (
        Income.query
        .filter(
            func.extract('year', Income.created_at) == now.year,
            func.extract('month', Income.created_at) == now.month,
        )
        .order_by(Income.created_at.desc())
        .all()
    )


def list_between_dates(start, end):
    return search_service.between_dates(SPEC, start, end)


def search(query):
    return search_service.search(SPEC, query)


def filter_incomes(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


# ------------------------------------------------------------------ helpers

def _account_for(is_cash, bank_account_id):
    """A cash income has no bank account; any other income needs one."""
    if is_cash:
        return None
    if not bank_account_id:
        raise NoBankProductSelected('You must select a bank account')
    return bank_account_id
