"""Withdrawals: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.withdrawal import Withdrawal
from app.services import withdrawal_service

RESOURCE = Resource(
    label='Withdrawal', model=Withdrawal, serialize=ser.withdrawal,
    create_schema=schemas.WithdrawalIn, create=withdrawal_service.create_withdrawal,
    update=withdrawal_service.update_withdrawal, delete=withdrawal_service.delete_withdrawal,
    default_list=withdrawal_service.list_all, filter=withdrawal_service.filter_withdrawals,
)
