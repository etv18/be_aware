"""Business rules for credit card payments.

A payment adds credit to a card (amount_available goes up). It is paid from a bank account, which
loses the money, or it is a cashback, which comes from nowhere and touches no account.
"""
from app.extensions import db
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.credit_card_payment import CreditCardPayment
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.exceptions.bankProductsException import BankAccountDoesNotExists
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=CreditCardPayment,
    joins=(CreditCardPayment.credit_card, CreditCardPayment.bank_account),
    text_columns=(CreditCardPayment.amount, CreditCard.nick_name, BankAccount.nick_name),
    extra_filter_columns=(CreditCardPayment.code,),
    keywords=(('cashback', 'bank', CreditCardPayment.is_cashback),),
)


def create_credit_card_payment(*, credit_card_id, amount, is_cashback=False, bank_account_id=None, created_at=None):
    amount = money.validate_amount(amount)
    bank_account_id = _account_for(is_cashback, bank_account_id)

    with atomic():
        card = money.get_credit_card(credit_card_id)

        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)
        money.give(card, amount)

        payment = CreditCardPayment(
            amount=amount,
            is_cashback=is_cashback,
            bank_account_id=bank_account_id,
            credit_card_id=card.id,
            created_at=created_at or utcnow(),
        )
        db.session.add(payment)
        db.session.flush()

        BankAccountTransactionsLedger.create(payment, commit=False)  # does nothing without a bank account
        CreditCardTransactionsLedger.create(payment, commit=False)

    return payment


def update_credit_card_payment(payment_id, *, amount, is_cashback=False, bank_account_id=None, created_at=None):
    amount = money.validate_amount(amount)
    bank_account_id = _account_for(is_cashback, bank_account_id)

    with atomic():
        payment = money.get_record(CreditCardPayment, payment_id, 'Credit card payment')
        card = payment.credit_card

        if payment.bank_account:
            money.give(payment.bank_account, payment.amount)  # the old payment never happened...
        if bank_account_id:
            money.take(money.get_bank_account(bank_account_id), amount)  # ...and the new one does

        card.amount_available += amount - payment.amount

        payment.amount = amount
        payment.is_cashback = is_cashback
        payment.bank_account_id = bank_account_id
        if created_at:
            payment.created_at = created_at

        db.session.flush()
        db.session.expire(payment, ['bank_account'])

        BankAccountTransactionsLedger.update(payment, commit=False)
        CreditCardTransactionsLedger.update(payment, commit=False)

    return payment


def delete_credit_card_payment(payment_id):
    with atomic():
        payment = money.get_record(CreditCardPayment, payment_id, 'Credit card payment')

        if payment.bank_account:
            money.give(payment.bank_account, payment.amount)  # the money goes back to the account
        payment.credit_card.amount_available -= payment.amount  # and the card loses the credit

        BankAccountTransactionsLedger.delete(payment, commit=False)
        CreditCardTransactionsLedger.delete(payment, commit=False)
        db.session.delete(payment)


def list_all():
    return CreditCardPayment.query.order_by(CreditCardPayment.created_at.desc()).all()


def filter_payments(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


def _account_for(is_cashback, bank_account_id):
    if is_cashback:
        return None
    if not bank_account_id:
        raise BankAccountDoesNotExists('You need to select a bank account.')
    return bank_account_id
