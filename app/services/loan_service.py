"""Business rules for loans: money lent to someone, taken from cash, a bank account or a credit card.

Payments received for a loan live in loan_payment_service. No Flask in here; every write runs in
atomic() so the loan, the balances and the ledger rows are saved together or not at all.
"""
from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.credit_card import CreditCard
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.models.loan import Loan
from app.models.loan_payment import LoanPayment
from app.exceptions.bankProductsException import NoBankProductSelected
from app.services import money, obligations, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=Loan,
    joins=(Loan.bank_account, Loan.credit_card),
    text_columns=(Loan.person_name, Loan.amount, Loan.description, BankAccount.nick_name),
    extra_filter_columns=(Loan.code, CreditCard.nick_name),
    keywords=(('yes', 'no', Loan.is_cash), ('active', 'paid', Loan.is_active)),
)


# ------------------------------------------------------------------ writes

def create_loan(*, amount, is_cash, person_name, description=None,
                bank_account_id=None, credit_card_id=None, created_at=None):
    amount = money.validate_amount(amount)

    if not is_cash and bank_account_id and credit_card_id:
        raise NoBankProductSelected('You cannot select both credit card and bank account.')
    if is_cash:
        bank_account_id = credit_card_id = None

    with atomic():
        if credit_card_id:
            money.take(money.get_credit_card(credit_card_id), amount)
        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)

        loan = Loan(
            amount=amount,
            is_cash=is_cash,
            person_name=person_name,
            bank_account_id=bank_account_id or None,
            credit_card_id=credit_card_id or None,
            description=description,
            created_at=created_at or utcnow(),
        )
        db.session.add(loan)
        db.session.flush()

        if loan.is_cash:
            CashLedger.create(loan, commit=False)
        if loan.bank_account_id:
            BankAccountTransactionsLedger.create(loan, commit=False)
        if loan.credit_card_id:
            CreditCardTransactionsLedger.create(loan, commit=False)

    return loan


def update_loan(loan_id, *, amount, is_cash, person_name, description=None, is_active=True,
                bank_account_id=None, credit_card_id=None, created_at=None):
    amount = money.validate_amount(amount)

    # when a bank account and a credit card both arrive, the bank account wins (as it always did)
    if is_cash:
        bank_account_id = credit_card_id = None
    elif bank_account_id:
        credit_card_id = None

    with atomic():
        loan = money.get_record(Loan, loan_id, 'Loan')

        _give_back(loan)
        if credit_card_id:
            money.take(money.get_credit_card(credit_card_id), amount)
        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)

        loan.amount = amount
        loan.is_cash = is_cash
        loan.person_name = person_name
        loan.description = description
        loan.bank_account_id = bank_account_id or None
        loan.credit_card_id = credit_card_id or None
        if created_at:
            loan.created_at = created_at

        db.session.flush()
        db.session.expire(loan, ['bank_account', 'credit_card'])

        if is_active:
            # not marked as paid by hand: it is active while the payments do not cover the amount
            obligations.refresh_status(loan, 'loan_payments', LoanPayment, LoanPayment.loan_id)
        else:
            loan.is_active = False  # marked as paid by hand, whatever is still unpaid
        CashLedger.update_or_delete(loan, delete_ledger=False, commit=False)
        BankAccountTransactionsLedger.update(loan, commit=False)
        CreditCardTransactionsLedger.update(loan, commit=False)

    return loan


def delete_loan(loan_id):
    """Delete a loan: give back what it took, undo the payments received for it, remove its ledgers."""
    with atomic():
        loan = money.get_record(Loan, loan_id, 'Loan')

        _give_back(loan)

        for payment in loan.loan_payments:
            if payment.bank_account:
                payment.bank_account.amount_available -= payment.amount
            BankAccountTransactionsLedger.delete(payment, commit=False)
            CashLedger.delete(payment, commit=False)

        BankAccountTransactionsLedger.delete(loan, commit=False)
        CreditCardTransactionsLedger.delete(loan, commit=False)
        CashLedger.delete(loan, commit=False)

        db.session.delete(loan)  # its payments go with it


# ------------------------------------------------------------------ reads

def list_all():
    return Loan.query.order_by(Loan.created_at.desc()).all()


def get_loan(loan_id):
    return money.get_record(Loan, loan_id, 'Loan')


def count_by_status():
    """{'actives': n, 'paids': n} over every loan."""
    return {
        'actives': Loan.query.filter(Loan.is_active == True).count(),   # noqa: E712
        'paids': Loan.query.filter(Loan.is_active == False).count(),    # noqa: E712
    }


def calculate_all_remainings():
    """What is still to collect: the unpaid part of every active loan."""
    return _remaining(Loan.query.filter(Loan.is_active == True).all())  # noqa: E712


def calculate_remainings(loans):
    """The same, for just the given loans (used when the page is filtered)."""
    return _remaining([loan for loan in loans if loan.is_active])


def count_active_and_paid(loans):
    return obligations.count_active_and_paid(loans)


def associated_records(loan_id):
    """{'loan_payment': [payment dicts]} for the loan (empty when it has no payments)."""
    loan = get_loan(loan_id)
    return {'loan_payment': [p.to_dict() for p in loan.loan_payments]} if loan.loan_payments else {}


def list_between_dates(start, end):
    return search_service.between_dates(SPEC, start, end)


def search(query):
    return search_service.search(SPEC, query)


def filter_loans(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


# ------------------------------------------------------------------ helpers

def _give_back(loan):
    """Return a loan's amount to the bank account or credit card it was taken from (cash has none)."""
    if loan.bank_account:
        money.give(loan.bank_account, loan.amount)
    if loan.credit_card:
        money.give(loan.credit_card, loan.amount)


def _remaining(loans):
    return obligations.remaining_of(loans, LoanPayment, LoanPayment.loan_id)
