"""Debt payments: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.debt_payment import DebtPayment
from app.services import debt_payment_service

RESOURCE = Resource(
    label='Debt payment', model=DebtPayment, serialize=ser.debt_payment,
    create_schema=schemas.DebtPaymentCreate, update_schema=schemas.DebtPaymentUpdate,
    create=debt_payment_service.create_debt_payment, update=debt_payment_service.update_debt_payment,
    delete=debt_payment_service.delete_debt_payment,
    default_list=debt_payment_service.list_all, filter=debt_payment_service.filter_debt_payments,
)
