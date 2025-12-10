from datetime import datetime
from sqlalchemy import func
from app.extensions import db

def generate_montly_sequence(prefix, model):
    now = datetime.now()
    year = now.year
    month = now.month

    #Count how many records of this models were create this moth
    last_number = (
        db.session.query(func.count(model.id))
        .filter(func.extract('year', model.created_at) == year)
        .filter(func.extract('month', model.created_at) == month)
        .scalar()
    )

    next_number = last_number + 1

    return f'{prefix}_{year}_{month:02d}_{next_number:05d}'
