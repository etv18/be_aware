"""Bank transfers: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.banktransfer import BankTransfer
from app.services import banktransfer_service

RESOURCE = Resource(
    label='Bank transfer', model=BankTransfer, serialize=ser.banktransfer,
    create_schema=schemas.BankTransferCreate, update_schema=schemas.BankTransferUpdate,
    create=banktransfer_service.create_banktransfer, update=banktransfer_service.update_banktransfer,
    delete=banktransfer_service.delete_banktransfer,
    default_list=banktransfer_service.list_all, filter=banktransfer_service.filter_transfers,
)
