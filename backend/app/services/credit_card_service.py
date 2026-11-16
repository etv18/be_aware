"""Business rules and reports for credit cards."""
from app.extensions import db
from app.models.credit_card import CreditCard
from app.models.credit_card_payment import CreditCardPayment
from app.models.expense import Expense
from app.models.loan import Loan
from app.services import associations, money
from app.utils.bank_accounts.filter_data import get_yearly_total_amount_info_by_filter_through_custom_model_and_fk
from app.utils.date_handling import MONTHS
from app.utils.filter_data import get_not_deleted_records
from app.utils.transactions import atomic


def create_credit_card(*, nick_name, amount_available, limit, bank_id):
    amount_available = money.validate_amount(amount_available)
    limit = money.validate_amount(limit)

    with atomic():
        credit_card = CreditCard(nick_name=nick_name, amount_available=amount_available, limit=limit, bank_id=bank_id)
        db.session.add(credit_card)

    return credit_card


def update_credit_card(card_id, *, nick_name, amount_available, limit, bank_id):
    amount_available = money.validate_amount(amount_available)
    limit = money.validate_amount(limit)

    with atomic():
        credit_card = money.get_record(CreditCard, card_id, 'Credit card')
        credit_card.nick_name = nick_name
        credit_card.limit = limit
        credit_card.amount_available = amount_available
        credit_card.bank_id = bank_id

    return credit_card


def delete_credit_card(card_id):
    """Credit cards are hidden, not removed, so their history stays readable."""
    with atomic():
        money.get_record(CreditCard, card_id, 'Credit card').is_deleted = True


def list_visible():
    return get_not_deleted_records(model=CreditCard)


def get_credit_card(card_id):
    return money.get_record(CreditCard, card_id, 'Credit card')


def money_used(credit_card):
    """How much of the card's limit is in use."""
    return credit_card.limit - credit_card.amount_available


def associated_records(card_id):
    card = get_credit_card(card_id)
    return associations.group_by_table(card.expenses, card.payments, card.loans)


def yearly_total_per_association(credit_card_id, year=None):
    info = {
        model.__tablename__: get_yearly_total_amount_info_by_filter_through_custom_model_and_fk(
            id=credit_card_id, CustomModel=model, fk_column_name='credit_card_id', year=year,
        )
        for model in (Expense, CreditCardPayment, Loan)
    }
    return {'months': MONTHS, 'associations_info': info}
