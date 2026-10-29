"""Loans: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource, list_response, payments_resource
from app.controllers.serializers import money
from app.models.loan import Loan
from app.services import loan_service


def _meta(records):
    return {**loan_service.count_active_and_paid(records), 'remaining': money(loan_service.calculate_remainings(records))}


RESOURCE = Resource(
    label='Loan', model=Loan, serialize=ser.loan,
    create_schema=schemas.LoanIn, update_schema=schemas.LoanUpdate, create=loan_service.create_loan,
    update=loan_service.update_loan, delete=loan_service.delete_loan,
    default_list=loan_service.list_all, filter=loan_service.filter_loans, list_meta=_meta,
)


def payments_of(loan_id):
    """The payments made on one loan."""
    return list_response(payments_resource(ser.loan_payment), list(loan_service.get_loan(loan_id).loan_payments))
