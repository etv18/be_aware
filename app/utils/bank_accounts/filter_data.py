import traceback
from datetime import datetime
from sqlalchemy import func, case
from decimal import Decimal

from app.extensions import db
from app.models.banktransfer import BankTransfer


''' MONTHLY REPORTS '''
def get_monthly_records(id, CustomModel, year, month) -> list:
    try:
        records = ( 
            CustomModel.query
            .filter(
                CustomModel.bank_account_id == id,
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

def get_monthly_total_amount_info(id, CustomModel, year, month) -> list:
    try:
        total_amount = ( 
            CustomModel.query
            .filter(
                CustomModel.bank_account_id == id,
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


def get_monthly_total_amount_info_of_transfers(id, year, month):
    try:
        outgoings_total_amount = ( 
            BankTransfer.query
            .filter(
                BankTransfer.from_bank_account_id == id,
                func.extract('year', BankTransfer.created_at) == year,
                func.extract('month', BankTransfer.created_at) == month
            )
            .with_entities(func.sum(BankTransfer.amount))
            .scalar() or Decimal(0.00)
        )
        
        incomings_total_amount = ( 
            BankTransfer.query
            .filter(
                BankTransfer.to_bank_account_id == id,
                func.extract('year', BankTransfer.created_at) == year,
                func.extract('month', BankTransfer.created_at) == month
            )
            .with_entities(func.sum(BankTransfer.amount))
            .scalar() or Decimal(0.00)
        )

        data = {
            'outgoings': outgoings_total_amount,
            'incomings': incomings_total_amount
        }

        return data
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e 

''' YEARLY REPORTS '''
def get_yearly_records(id, CustomModel, year=None) -> list:
    if year is None:
        year = datetime.now().year

    monthly_records = []

    for month in range(1, 13):
        record = get_monthly_records(
            id=id,
            CustomModel=CustomModel, 
            year=year,
            month=month
        )
        monthly_records.append(record)
    
    return monthly_records

def get_yearly_total_amount_info(id, CustomModel, year=None) -> list:
    try:
        if year is None:
            year = datetime.now().year

        results = (
            CustomModel.query
            .filter(
                CustomModel.bank_account_id == id,
                func.extract('year', CustomModel.created_at) == year
            )
            .with_entities(
                func.extract('month', CustomModel.created_at).label('month'),
                func.sum(CustomModel.amount).label('total')
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

def get_yearly_total_amount_info_of_transfers(id, year=None) -> list:
    try:
        if year is None:
            year = datetime.now().year

        results = (
            BankTransfer.query
            .filter(
                func.extract('year', BankTransfer.created_at) == year,
                (BankTransfer.from_bank_account_id == id) |
                (BankTransfer.to_bank_account_id == id)
            )
            .with_entities(
                func.extract('month', BankTransfer.created_at).label('month'),

                func.sum(
                    case(
                        (BankTransfer.from_bank_account_id == id, BankTransfer.amount),
                        else_=0
                    )
                ).label('outgoings'),

                func.sum(
                    case(
                        (BankTransfer.to_bank_account_id == id, BankTransfer.amount),
                        else_=0
                    )
                ).label('incomings'),
            )
            .group_by('month')
            .all()
        )

        # Initialize all 12 months with 0
        outgoings = {m: Decimal('0.00') for m in range(1, 13)}
        incomings = {m: Decimal('0.00') for m in range(1, 13)}

        for month, outgoing, incoming in results:
            month = int(month)
            outgoings[month] = outgoing or Decimal('0.00')
            incomings[month] = incoming or Decimal('0.00')

        return {
            'outgoings': [outgoings[m] for m in range(1, 13)],
            'incomings': [incomings[m] for m in range(1, 13)],
        }

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e