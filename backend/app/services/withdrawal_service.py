"""Business rules for withdrawals: money leaves a bank account and becomes cash."""
from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.withdrawal import Withdrawal
from app.exceptions.bankProductsException import NoBankProductSelected
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=Withdrawal,
    joins=(Withdrawal.bank_account,),
    text_columns=(Withdrawal.amount, Withdrawal.description, BankAccount.nick_name),
    extra_filter_columns=(Withdrawal.code,),
)


def create_withdrawal(*, amount, bank_account_id, description=None, created_at=None):
    amount = money.validate_amount(amount)

    with atomic():
        account = _get_account(bank_account_id)
        money.take(account, amount)

        withdrawal = Withdrawal(
            amount=amount,
            description=description,
            bank_account_id=account.id,
            created_at=created_at or utcnow(),
        )
        db.session.add(withdrawal)
        db.session.flush()

        CashLedger.create(withdrawal, commit=False)
        BankAccountTransactionsLedger.create(withdrawal, commit=False)

    return withdrawal


def update_withdrawal(withdrawal_id, *, amount, bank_account_id, description=None, created_at=None):
    amount = money.validate_amount(amount)

    with atomic():
        withdrawal = money.get_record(Withdrawal, withdrawal_id, 'Withdrawal')
        account = _get_account(bank_account_id)

        money.give(withdrawal.bank_account, withdrawal.amount)  # the old withdrawal never happened...
        money.take(account, amount)                             # ...and the new one does

        withdrawal.amount = amount
        withdrawal.description = description
        withdrawal.bank_account_id = account.id
        if created_at:
            withdrawal.created_at = created_at

        db.session.flush()
        db.session.expire(withdrawal, ['bank_account'])

        CashLedger.update_or_delete(withdrawal, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(withdrawal, commit=False)

    return withdrawal


def delete_withdrawal(withdrawal_id):
    with atomic():
        withdrawal = money.get_record(Withdrawal, withdrawal_id, 'Withdrawal')

        money.give(withdrawal.bank_account, withdrawal.amount)

        CashLedger.delete(withdrawal, commit=False)
        BankAccountTransactionsLedger.delete(withdrawal, commit=False)
        db.session.delete(withdrawal)


def list_all():
    return Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()


def list_between_dates(start, end):
    return search_service.between_dates(SPEC, start, end)


def search(query):
    return search_service.search(SPEC, query)


def filter_withdrawals(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


def _get_account(bank_account_id):
    if not bank_account_id:
        raise NoBankProductSelected('No bank account was selected for this withdrawal')
    return money.get_bank_account(bank_account_id)
