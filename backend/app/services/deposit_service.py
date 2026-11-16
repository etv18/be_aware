"""Business rules for deposits: cash goes into a bank account."""
from decimal import Decimal

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.deposit import Deposit
from app.exceptions.bankProductsException import AmountGreaterThanAvailableMoney, NoBankProductSelected
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.filter_data import get_total_amount
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=Deposit,
    joins=(Deposit.bank_account,),
    text_columns=(Deposit.amount, Deposit.description, BankAccount.nick_name),
    extra_filter_columns=(Deposit.code,),
)


def create_deposit(*, amount, bank_account_id, description=None, created_at=None):
    amount = money.validate_amount(amount)

    with atomic():
        account = _get_account(bank_account_id)
        _require_cash(amount)

        money.give(account, amount)

        deposit = Deposit(
            amount=amount,
            description=description,
            bank_account_id=account.id,
            created_at=created_at or utcnow(),
        )
        db.session.add(deposit)
        db.session.flush()

        CashLedger.create(deposit, commit=False)
        BankAccountTransactionsLedger.create(deposit, commit=False)

    return deposit


def update_deposit(deposit_id, *, amount, bank_account_id, description=None, created_at=None):
    amount = money.validate_amount(amount)

    with atomic():
        deposit = money.get_record(Deposit, deposit_id, 'Deposit')
        account = _get_account(bank_account_id)

        _take_back(deposit)                                   # the old deposit never happened...
        _require_cash(amount, already_counted=deposit.amount)  # ...so its cash is available again
        money.give(account, amount)                           # ...and the new one does

        deposit.amount = amount
        deposit.description = description
        deposit.bank_account_id = account.id
        if created_at:
            deposit.created_at = created_at

        db.session.flush()
        db.session.expire(deposit, ['bank_account'])

        CashLedger.update_or_delete(deposit, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(deposit, commit=False)

    return deposit


def delete_deposit(deposit_id):
    with atomic():
        deposit = money.get_record(Deposit, deposit_id, 'Deposit')

        _take_back(deposit)

        CashLedger.delete(deposit, commit=False)
        BankAccountTransactionsLedger.delete(deposit, commit=False)
        db.session.delete(deposit)


def list_all():
    return Deposit.query.order_by(Deposit.created_at.desc()).all()


def list_between_dates(start, end):
    return search_service.between_dates(SPEC, start, end)


def search(query):
    return search_service.search(SPEC, query)


def filter_deposits(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


# ------------------------------------------------------------------ helpers

def _get_account(bank_account_id):
    if not bank_account_id:
        raise NoBankProductSelected('No bank account was selected for this deposit')
    return money.get_bank_account(bank_account_id)


def _require_cash(amount, already_counted=Decimal()):
    """Cash in hand is the sum of the cash ledger. `already_counted` is cash a deposit being
    edited has already taken out of it."""
    available = get_total_amount(CashLedger) + already_counted
    if amount > available:
        raise AmountGreaterThanAvailableMoney('You do not have enough cash available for this deposit')


def _take_back(deposit):
    """Take a deposit's money back out of its bank account, refusing to leave it below zero."""
    account = deposit.bank_account
    if account.amount_available < deposit.amount:
        raise AmountGreaterThanAvailableMoney(
            f"Insufficient founds from '{account.nick_name}' bank account to change or delete this deposit."
        )
    account.amount_available -= deposit.amount
