"""Banks: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.bank import Bank
from app.services import bank_service

RESOURCE = Resource(
    label='Bank', model=Bank, serialize=ser.bank, has_amount=False,
    create_schema=schemas.BankIn, create=bank_service.create_bank,
    update=bank_service.update_bank, delete=bank_service.delete_bank,
    default_list=bank_service.list_banks,
)
