from app.extensions import db
from decimal import Decimal

def get_total_amount(model, field_name='amount'):
    total = db.session.query(
        db.func.sum(getattr(model, field_name))    
    ).scalar() or Decimal('0')
    return total
