from datetime import datetime
from sqlalchemy import extract, func

def get_monthly_records(CustomModel, year, month):
    
    records = ( 
        CustomModel.query
        .filter(
            extract('year', CustomModel.created_at) == year,
            extract('month', CustomModel.created_at) == month
        )
        .order_by(CustomModel.created_at.desc())
        .all()
    )
    return records

def get_yearly_records(CustomModel, year=None):
    if year is None:
        year = datetime.now().year

    monthly_records = []

    for month in range(1, 13):
        record = get_monthly_records(
            CustomModel=CustomModel, 
            year=year
        )
        monthly_records.append(record)
    
    return monthly_records

