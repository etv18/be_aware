"""Debts: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource, list_response, payments_resource
from app.controllers.serializers import money
from app.models.debt import Debt
from app.services import debt_service


def _meta(records):
    return {**debt_service.count_active_and_paid(records), 'remaining': money(debt_service.calculate_remainings(records))}


RESOURCE = Resource(
    label='Debt', model=Debt, serialize=ser.debt,
    create_schema=schemas.DebtIn, update_schema=schemas.DebtUpdate, create=debt_service.create_debt,
    update=debt_service.update_debt, delete=debt_service.delete_debt,
    default_list=debt_service.list_all, filter=debt_service.filter_debts, list_meta=_meta,
)


def payments_of(debt_id):
    """The payments made on one debt."""
    return list_response(payments_resource(ser.debt_payment), list(debt_service.get_debt(debt_id).debt_payments))
