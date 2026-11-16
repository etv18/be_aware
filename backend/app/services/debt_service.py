"""Business rules for debts: money borrowed from someone, received as cash or into a bank account.

Payments made for a debt live in debt_payment_service. No Flask in here; every write runs in
atomic() so the debt, the balances and the ledger rows are saved together or not at all.
"""
from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.services import money, obligations, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=Debt,
    joins=(Debt.bank_account,),
    text_columns=(Debt.person_name, Debt.amount, Debt.description, BankAccount.nick_name),
    extra_filter_columns=(Debt.code,),
    keywords=(('yes', 'no', Debt.is_cash), ('active', 'paid', Debt.is_active)),
)


# ------------------------------------------------------------------ writes

def create_debt(*, amount, is_cash, person_name, description=None, bank_account_id=None, created_at=None):
    """A debt that is not cash may have no bank account; then it moves no money at all."""
    amount = money.validate_amount(amount)
    if is_cash:
        bank_account_id = None

    with atomic():
        if bank_account_id:
            money.give(money.get_bank_account(bank_account_id), amount)

        debt = Debt(
            amount=amount,
            is_cash=is_cash,
            person_name=person_name,
            bank_account_id=bank_account_id or None,
            description=description,
            created_at=created_at or utcnow(),
        )
        db.session.add(debt)
        db.session.flush()

        if debt.is_cash:
            CashLedger.create(debt, commit=False)
        if debt.bank_account_id:
            BankAccountTransactionsLedger.create(debt, commit=False)

    return debt


def update_debt(debt_id, *, amount, is_cash, person_name, description=None, is_active=True,
                bank_account_id=None, created_at=None):
    amount = money.validate_amount(amount)
    if is_cash:
        bank_account_id = None

    with atomic():
        debt = money.get_record(Debt, debt_id, 'Debt')

        if debt.bank_account:
            debt.bank_account.amount_available -= debt.amount  # the money it brought in goes back out
        if bank_account_id:
            money.give(money.get_bank_account(bank_account_id), amount)

        debt.amount = amount
        debt.is_cash = is_cash
        debt.person_name = person_name
        debt.description = description
        debt.bank_account_id = bank_account_id or None
        if created_at:
            debt.created_at = created_at

        db.session.flush()
        db.session.expire(debt, ['bank_account'])

        if is_active:
            # not marked as paid by hand: it is active while the payments do not cover the amount
            obligations.refresh_status(debt, 'debt_payments', DebtPayment, DebtPayment.debt_id)
        else:
            debt.is_active = False  # marked as paid by hand, whatever is still unpaid
        CashLedger.update_or_delete(debt, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(debt, commit=False)

    return debt


def delete_debt(debt_id):
    """Delete a debt: take back the money it brought in, undo the payments made for it, remove its ledgers."""
    with atomic():
        debt = money.get_record(Debt, debt_id, 'Debt')

        for payment in debt.debt_payments:
            if payment.bank_account:
                money.give(payment.bank_account, payment.amount)
            BankAccountTransactionsLedger.delete(payment, commit=False)
            CashLedger.delete(payment, commit=False)

        if debt.bank_account:
            debt.bank_account.amount_available -= debt.amount
        BankAccountTransactionsLedger.delete(debt, commit=False)
        CashLedger.delete(debt, commit=False)

        db.session.delete(debt)  # its payments go with it


# ------------------------------------------------------------------ reads

def list_all():
    return Debt.query.order_by(Debt.created_at.desc()).all()


def get_debt(debt_id):
    return money.get_record(Debt, debt_id, 'Debt')


def count_by_status():
    return {
        'actives': Debt.query.filter(Debt.is_active == True).count(),   # noqa: E712
        'paids': Debt.query.filter(Debt.is_active == False).count(),    # noqa: E712
    }


def calculate_all_remainings():
    """What is still to pay: the unpaid part of every active debt."""
    return _remaining(Debt.query.filter(Debt.is_active == True).all())  # noqa: E712


def calculate_remainings(debts):
    return _remaining([debt for debt in debts if debt.is_active])


def count_active_and_paid(debts):
    return obligations.count_active_and_paid(debts)


def associated_records(debt_id):
    """{'debt_payments': [payment dicts]} for the debt (empty when it has no payments)."""
    debt = get_debt(debt_id)
    return {'debt_payments': [p.to_dict() for p in debt.debt_payments]} if debt.debt_payments else {}


def list_between_dates(start, end):
    return search_service.between_dates(SPEC, start, end)


def search(query):
    return search_service.search(SPEC, query)


def filter_debts(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


def _remaining(debts):
    return obligations.remaining_of(debts, DebtPayment, DebtPayment.debt_id)
