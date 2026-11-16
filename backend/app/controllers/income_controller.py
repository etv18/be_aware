"""Incomes: JSON in, service call, JSON out."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource
from app.models.income import Income
from app.services import income_service

RESOURCE = Resource(
    label='Income', model=Income, serialize=ser.income,
    create_schema=schemas.IncomeIn, create=income_service.create_income,
    update=income_service.update_income, delete=income_service.delete_income,
    default_list=income_service.get_monthly_incomes_records,
    filter=income_service.filter_incomes, stored_as_utc=False,
)
