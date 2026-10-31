"""Small building blocks every money service shares: amount validation, loading bank products and
moving money in or out of them.

Nothing here commits. Callers wrap their work in app.utils.transactions.atomic().
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.exceptions.bankProductsException import (
    AmountGreaterThanAvailableMoney,
    AmountIsLessThanOrEqualsToZero,
    BankAccountDoesNotExists,
    CreditCardDoesNotExists,
    NoAvailableMoney,
)
from app.exceptions.records import RecordNotFound

CENTS = Decimal('0.01')


def validate_amount(amount):
    """Return `amount` as a Decimal rounded to cents, or raise if it is not a number above zero."""
    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError, ValueError):
        raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

    if not amount.is_finite():
        raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

    amount = amount.quantize(CENTS, rounding=ROUND_HALF_UP)  # the database keeps cents only

    if amount <= 0:
        raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

    return amount


def get_record(model, record_id, label):
    """Load a record by id or raise RecordNotFound('<label> not found')."""
    record = db.session.get(model, record_id) if record_id is not None else None
    if not record:
        raise RecordNotFound(f'{label} not found')
    return record


def get_bank_account(account_id):
    account = db.session.get(BankAccount, account_id) if account_id else None
    if not account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    return account


def get_credit_card(card_id):
    card = db.session.get(CreditCard, card_id) if card_id else None
    if not card:
        raise CreditCardDoesNotExists('This credit card does not exists.')
    return card


def take(product, amount):
    """Take `amount` out of a bank account or credit card, refusing to go below zero."""
    if product.amount_available <= 0:
        kind = 'Bank Account' if isinstance(product, BankAccount) else 'Credit card'
        raise NoAvailableMoney(f'{kind} does not have any money left.')
    if product.amount_available < amount:
        raise AmountGreaterThanAvailableMoney('Insufficient founds.')

    product.amount_available -= amount


def give(product, amount):
    """Put `amount` into a bank account or credit card."""
    product.amount_available += amount
