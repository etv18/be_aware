"""Loan payments: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.loan_payment import LoanPayment
from app.services import loan_payment_service

RESOURCE = Resource(
    label='Loan payment', model=LoanPayment, serialize=ser.loan_payment,
    create_schema=schemas.LoanPaymentCreate, update_schema=schemas.LoanPaymentUpdate,
    create=loan_payment_service.create_loan_payment, update=loan_payment_service.update_loan_payment,
    delete=loan_payment_service.delete_loan_payment,
    default_list=loan_payment_service.list_all, filter=loan_payment_service.filter_loan_payments,
)
