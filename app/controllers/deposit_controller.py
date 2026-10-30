"""Deposits: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.deposit import Deposit
from app.services import deposit_service

RESOURCE = Resource(
    label='Deposit', model=Deposit, serialize=ser.deposit,
    create_schema=schemas.DepositIn, create=deposit_service.create_deposit,
    update=deposit_service.update_deposit, delete=deposit_service.delete_deposit,
    default_list=deposit_service.list_all, filter=deposit_service.filter_deposits,
)
