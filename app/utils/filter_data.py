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

