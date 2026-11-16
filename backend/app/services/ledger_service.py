"""The three ledgers (cash, bank account, credit card): read access and the cash adjustments.

Ledger rows are written by the money services (income_service, expense_service, ...), never by
hand, with one exception: a cash adjustment, which fixes the cash total when the wallet and the
app disagree.
"""
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger as BankLedger
from app.models.cash_ledger import CashLedger
from app.models.credit_card import CreditCard
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger as CardLedger
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.exceptions.records import RecordNotFound
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.code_generator import generate_montly_sequence
from app.utils.date_handling import utcnow
from app.utils.prefixes import ADJUSTMENT
from app.utils.transactions import atomic

ADJUSTMENT_TYPE = 'ADJUSTMENT'


def _as_text(column):
    return db.cast(column, db.String)


CASH_SPEC = SearchSpec(
    model=CashLedger,
    text_columns=(CashLedger.amount, CashLedger.type, CashLedger.reference_code),
    extra_filter_columns=(_as_text(CashLedger.created_at),),
)

BANK_SPEC = SearchSpec(
    model=BankLedger,
    joins=(BankLedger.bank_account,),
    text_columns=(
        _as_text(BankLedger.amount), _as_text(BankLedger.before_update_balance), _as_text(BankLedger.after_update_balance),
        BankLedger.reference_code, BankLedger.transaction_type, _as_text(BankLedger.created_at), BankAccount.nick_name,
    ),
    pair_columns=(BankAccount.nick_name, BankLedger.transaction_type),
)

CARD_SPEC = SearchSpec(
    model=CardLedger,
    joins=(CardLedger.credit_card,),
    text_columns=(
        _as_text(CardLedger.amount), _as_text(CardLedger.before_update_balance), _as_text(CardLedger.after_update_balance),
        CardLedger.reference_code, CardLedger.transaction_type, _as_text(CardLedger.created_at), CreditCard.nick_name,
    ),
    pair_columns=(CreditCard.nick_name, CardLedger.transaction_type),
)


# ------------------------------------------------------------------ cash adjustments

def create_cash_adjustment(*, amount, created_at=None):
    """Add (positive) or take away (negative) cash without a transaction behind it."""
    amount = _parse_adjustment(amount)

    with atomic():
        ledger = CashLedger(
            amount=amount,
            type=ADJUSTMENT_TYPE,
            reference_code=generate_montly_sequence(prefix=ADJUSTMENT, model=CashLedger, field_name='reference_code'),
            created_at=created_at or utcnow(),
        )
        db.session.add(ledger)

    return ledger


def delete_cash_adjustment(ledger_id):
    """Only adjustments can be removed; every other cash ledger row belongs to a transaction."""
    with atomic():
        ledger = money.get_record(CashLedger, ledger_id, 'Adjustment')
        if ledger.type.lower() != ADJUSTMENT_TYPE.lower():
            raise ValueError('Only adjustments can be deleted.')
        db.session.delete(ledger)


def _parse_adjustment(amount):
    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError, ValueError):
        raise AmountIsLessThanOrEqualsToZero('Introduce a valid number')

    amount = amount.quantize(money.CENTS) if amount.is_finite() else amount
    if not amount.is_finite() or amount == 0:
        raise AmountIsLessThanOrEqualsToZero('Introduce a valid number')

    return amount


# ------------------------------------------------------------------ reads

def cash_balance():
    return db.session.query(db.func.sum(CashLedger.amount)).scalar() or 0


def list_cash():
    return CashLedger.query.order_by(CashLedger.created_at.desc()).all()


def list_bank():
    return BankLedger.query.order_by(BankLedger.created_at.desc()).all()


def list_card():
    return CardLedger.query.order_by(CardLedger.created_at.desc()).all()


def between_dates(spec, start, end):
    return search_service.between_dates(spec, start, end)


def search(spec, query):
    return search_service.search(spec, query)


def filter_ledger(spec, query=None, start=None, end=None):
    return search_service.filter_all(spec, query, start, end)
