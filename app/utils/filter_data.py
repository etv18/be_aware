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

def get_yearly_total_amount_info_using_source(CustomModel, year=None, source=None) -> list:
    try:
        #This will return a yearly report of records which used either a credit card or a bank account
        if year is None:
            year = datetime.now().year

        query = CustomModel.query.filter(
            db.func.extract('year', CustomModel.created_at) == year
        )

        # Apply exclusive source filter
        if source == "bank":
            query = query.filter(CustomModel.bank_account_id.isnot(None))
        elif source == "card":
            query = query.filter(CustomModel.credit_card_id.isnot(None))
        elif source == 'cash':
            query = query.filter(CustomModel.is_cash.isnot(False))


        results = (
            query
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

        return [monthly_totals[m] for m in range(1, 13)]

    except Exception:
        db.session.rollback()
        traceback.print_exc()
        raise


def get_monthly_total_amount_info(CustomModel, year, month) -> Decimal:
    try:
        return CustomModel.query.filter(
            db.extract('year', CustomModel.created_at) == year,
            db.extract('month', CustomModel.created_at) == month
        ).with_entities(db.func.sum(CustomModel.amount)).scalar() or Decimal(0.00)
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
    
def get_active_records(model):
    keep_executing = getattr(model, 'is_active', False)
    if not keep_executing : return None

    return (
        model.query
        .filter(model.is_active == True)
        .all()
    )

def get_not_deleted_records(model):
    keep_executing = getattr(model, 'is_deleted', False)
    if not keep_executing : return None

    return (
        model.query
        .filter(model.is_deleted == False)
        .all()
    )
