import traceback
from datetime import datetime
from sqlalchemy import func
from decimal import Decimal

from app.extensions import db

def get_monthly_records(CustomModel, year, month) -> list:
    try:
        records = ( 
            CustomModel.query
            .filter(
                func.extract('year', CustomModel.created_at) == year,
                func.extract('month', CustomModel.created_at) == month
            )
            .order_by(CustomModel.created_at.desc())
            .all()
        )
        return records
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e

def get_monthly_total_amount_info(CustomModel, year, month) -> list:
    try:
        total_amount = ( 
            CustomModel.query
            .filter(
                func.extract('year', CustomModel.created_at) == year,
                func.extract('month', CustomModel.created_at) == month
            )
            .with_entities(func.sum(CustomModel.amount))
            .scalar() or Decimal(0.00)
        )
        return total_amount
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e

def get_yearly_records(CustomModel, year=None) -> list:
    if year is None:
        year = datetime.now().year

    monthly_records = []

    for month in range(1, 13):
        record = get_monthly_records(
            CustomModel=CustomModel, 
            year=year,
            month=month
        )
        monthly_records.append(record)
    
    return monthly_records

def get_yearly_total_amount_info(CustomModel, year=None) -> list:
    if year is None:
        year = datetime.now().year

    monthly_totals = []

    for month in range(1, 13):
        record = get_monthly_total_amount_info(
            CustomModel=CustomModel, 
            year=year,
            month=month
        )
        monthly_totals.append(record)
    
    return monthly_totals