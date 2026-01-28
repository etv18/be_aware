from app.extensions import db
from decimal import Decimal
from datetime import datetime
import traceback

def get_total_amount(model, field_name='amount'):
    total = db.session.query(
        db.func.sum(getattr(model, field_name))    
    ).scalar() or Decimal('0')
    return total

def get_yearly_total_amount_info(CustomModel, year=None) -> list:
    try:
        if year is None:
            year = datetime.now().year

        results = (
            CustomModel.query
            .filter(
                db.func.extract('year', CustomModel.created_at) == year
            )
            .with_entities(
                db.func.extract('month', CustomModel.created_at).label('month'),
                db.func.sum(CustomModel.amount).label('total')
            )
            .group_by('month')
            .all()
        )

        # Initialize all 12 months with 0
        monthly_totals = {month: Decimal('0.00') for month in range(1, 13)}

        # Fill months that have data
        for month, total in results:
            monthly_totals[int(month)] = total or Decimal('0.00')

        # Return ordered list (Jan → Dec)
        return [monthly_totals[m] for m in range(1, 13)]

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e