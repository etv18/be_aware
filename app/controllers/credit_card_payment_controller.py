"""Credit card payments: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.credit_card_payment import CreditCardPayment
from app.services import credit_card_payment_service

RESOURCE = Resource(
    label='Credit card payment', model=CreditCardPayment, serialize=ser.credit_card_payment,
    create_schema=schemas.CreditCardPaymentCreate, update_schema=schemas.CreditCardPaymentUpdate,
    create=credit_card_payment_service.create_credit_card_payment,
    update=credit_card_payment_service.update_credit_card_payment,
    delete=credit_card_payment_service.delete_credit_card_payment,
    default_list=credit_card_payment_service.list_all, filter=credit_card_payment_service.filter_payments,
)
