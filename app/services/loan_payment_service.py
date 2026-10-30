"""Business rules for loan payments: money coming back for a loan, into cash or a bank account."""
from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.loan import Loan
from app.models.loan_payment import LoanPayment
from app.exceptions.bankProductsException import NoBankProductSelected
from app.exceptions.records import LoanAlreadyPaid, MarkedAsPaid
from app.services import money, obligations, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=LoanPayment,
    joins=(LoanPayment.bank_account,),
    text_columns=(LoanPayment.amount, BankAccount.nick_name),
    extra_filter_columns=(LoanPayment.code,),
    keywords=(('yes', 'no', LoanPayment.is_cash),),
)


def create_loan_payment(*, loan_id, amount, is_cash, bank_account_id=None, created_at=None):
    """Register a payment. Raises LoanAlreadyPaid when the loan was already covered."""
    with atomic():
        loan = money.get_record(Loan, loan_id, 'Loan')

        if _total_paid(loan) >= loan.amount:
            raise LoanAlreadyPaid('Loan is already fully paid')

        # Checks if the loan is no longer active even though it's not fully paid
        if not loan.is_active:
            raise MarkedAsPaid('Status indicates this loan is paid')

        amount = money.validate_amount(amount)
        bank_account_id = _account_for(is_cash, bank_account_id)

        if bank_account_id:
            money.give(money.get_bank_account(bank_account_id), amount)

        payment = LoanPayment(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id,
            loan_id=loan.id,
            created_at=created_at or utcnow(),
        )
        db.session.add(payment)
        db.session.flush()

        if payment.is_cash:
            CashLedger.create(payment, commit=False)
        if payment.bank_account_id:
            BankAccountTransactionsLedger.create(payment, commit=False)

        _refresh_loan_status(loan)

    return payment


def update_loan_payment(payment_id, *, amount, is_cash, bank_account_id=None, created_at=None):
    amount = money.validate_amount(amount)
    bank_account_id = _account_for(is_cash, bank_account_id)

    with atomic():
        payment = money.get_record(LoanPayment, payment_id, 'Loan payment')

        if payment.bank_account:
            payment.bank_account.amount_available -= payment.amount  # take the old payment back out
        if bank_account_id:
            money.give(money.get_bank_account(bank_account_id), amount)

        payment.amount = amount
        payment.is_cash = is_cash
        payment.bank_account_id = bank_account_id
        if created_at:
            payment.created_at = created_at

        db.session.flush()
        db.session.expire(payment, ['bank_account'])

        CashLedger.update_or_delete(payment, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(payment, commit=False)

        _refresh_loan_status(payment.loan)

    return payment


def delete_loan_payment(payment_id):
    with atomic():
        payment = money.get_record(LoanPayment, payment_id, 'Loan payment')
        loan = payment.loan

        if payment.bank_account:
            payment.bank_account.amount_available -= payment.amount

        BankAccountTransactionsLedger.delete(payment, commit=False)
        CashLedger.delete(payment, commit=False)
        db.session.delete(payment)
        db.session.flush()

        _refresh_loan_status(loan)


def list_all():
    return LoanPayment.query.order_by(LoanPayment.created_at.desc()).all()


def filter_loan_payments(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


# ------------------------------------------------------------------ helpers

def _account_for(is_cash, bank_account_id):
    if is_cash:
        return None
    if not bank_account_id:
        raise NoBankProductSelected('You must select a bank account')
    return bank_account_id


def _total_paid(loan):
    return obligations.total_paid(loan, LoanPayment, LoanPayment.loan_id)


def _refresh_loan_status(loan):
    obligations.refresh_status(loan, 'loan_payments', LoanPayment, LoanPayment.loan_id)
