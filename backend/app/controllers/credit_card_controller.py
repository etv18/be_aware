"""Credit cards: JSON in, service call, JSON out; plus what hangs from a card and its report."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource, data, year_param
from app.models.credit_card import CreditCard
from app.services import credit_card_service

RESOURCE = Resource(
    label='Credit card', model=CreditCard, serialize=ser.credit_card, has_amount=False,
    create_schema=schemas.CreditCardIn, create=credit_card_service.create_credit_card,
    update=credit_card_service.update_credit_card, delete=credit_card_service.delete_credit_card,
    default_list=credit_card_service.list_visible,
)


def records_of(card_id):
    card = credit_card_service.get_credit_card(card_id)
    return data({'credit_card': ser.credit_card(card),
                 'records': ser.group_by_table(card.expenses, card.payments, card.loans)})


def yearly_report(card_id):
    credit_card_service.get_credit_card(card_id)
    return data(credit_card_service.yearly_total_per_association(card_id, year_param()))
