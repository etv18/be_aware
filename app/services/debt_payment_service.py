"""Business rules for debt payments: money paid back for a debt, from cash or a bank account."""
from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.exceptions.bankProductsException import NoBankProductSelected
from app.exceptions.records import DebtAlreadyPaid
from app.services import money, obligations, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=DebtPayment,
    joins=(DebtPayment.bank_account,),
    text_columns=(DebtPayment.amount, BankAccount.nick_name),
    extra_filter_columns=(DebtPayment.code,),
    keywords=(('yes', 'no', DebtPayment.is_cash),),
)


def create_debt_payment(*, debt_id, amount, is_cash, bank_account_id=None, created_at=None):
    """Register a payment. Raises DebtAlreadyPaid when the debt was already covered."""
    with atomic():
        debt = money.get_record(Debt, debt_id, 'Debt')

        if _total_paid(debt) >= debt.amount:
            raise DebtAlreadyPaid('Debt is already fully paid')

        amount = money.validate_amount(amount)
        bank_account_id = _account_for(is_cash, bank_account_id)

        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)

        payment = DebtPayment(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id,
            debt_id=debt.id,
            created_at=created_at or utcnow(),
        )
        db.session.add(payment)
        db.session.flush()

        if payment.is_cash:
            CashLedger.create(payment, commit=False)
        if payment.bank_account_id:
            BankAccountTransactionsLedger.create(payment, commit=False)

        _refresh_debt_status(debt)

    return payment


def update_debt_payment(payment_id, *, amount, is_cash, bank_account_id=None, created_at=None):
    amount = money.validate_amount(amount)
    bank_account_id = _account_for(is_cash, bank_account_id)

    with atomic():
        payment = money.get_record(DebtPayment, payment_id, 'Debt payment')

        if payment.bank_account:
            money.give(payment.bank_account, payment.amount)  # the old payment never happened...
        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)  # ...and the new one does

        payment.amount = amount
        payment.is_cash = is_cash
        payment.bank_account_id = bank_account_id
        if created_at:
            payment.created_at = created_at

        db.session.flush()
        db.session.expire(payment, ['bank_account'])

        CashLedger.update_or_delete(payment, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(payment, commit=False)

        _refresh_debt_status(payment.debt)

    return payment


def delete_debt_payment(payment_id):
    with atomic():
        payment = money.get_record(DebtPayment, payment_id, 'Debt payment')
        debt = payment.debt

        if payment.bank_account:
            money.give(payment.bank_account, payment.amount)

        BankAccountTransactionsLedger.delete(payment, commit=False)
        CashLedger.delete(payment, commit=False)
        db.session.delete(payment)

        _refresh_debt_status(debt)


def list_all():
    return DebtPayment.query.order_by(DebtPayment.created_at.desc()).all()


def filter_debt_payments(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


# ------------------------------------------------------------------ helpers

def _account_for(is_cash, bank_account_id):
    if is_cash:
        return None
    if not bank_account_id:
        raise NoBankProductSelected('Please select a bank account')
    return bank_account_id


def _total_paid(debt):
    return obligations.total_paid(debt, DebtPayment, DebtPayment.debt_id)


def _refresh_debt_status(debt):
    obligations.refresh_status(debt, 'debt_payments', DebtPayment, DebtPayment.debt_id)
