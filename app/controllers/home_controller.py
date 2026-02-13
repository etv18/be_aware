from flask import request, current_app as ca

from sqlalchemy import extract, func

from decimal import Decimal
from datetime import datetime

from app.extensions import db
from app.models.expense import Expense
from app.models.income import Income

def get_monthly_income_and_expense_data():
    try:
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        total_amount_expenses = h_get_monthly_records(Expense, current_year, current_month)
        total_amount_incomes = h_get_monthly_records(Income, current_year, current_month)
    except Exception as e:
        print(e)
        ca.logger.exception(f"Unexpected error getting monthly income and expense data for year {current_year} and month {current_month}")
        raise e
    
    return {'incomes': total_amount_incomes, 'expenses': total_amount_expenses}

def get_yearly_income_and_expense_data():
    data = {}
    try:
        now = datetime.now()
        current_year = now.year

        total_amount_expenses_per_month = h_get_yearly_records(Expense, current_year)
        total_amount_incomes_per_month = h_get_yearly_records(Income, current_year)
        
        data = {
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'expenses': total_amount_expenses_per_month,
            'incomes': total_amount_incomes_per_month,
        }
    except Exception as e:
        print(e)
        ca.logger.exception(f"Unexpected error getting yearly income and expense data for year {current_year}")
        raise e
    
    return data


def h_get_monthly_records(CustomModel, current_year, current_month):

    records = CustomModel.query.filter(
        extract('year', CustomModel.created_at) == current_year,
        extract('month', CustomModel.created_at) == current_month
    ).with_entities(func.sum(CustomModel.amount)).scalar() or Decimal(0.00)
 
    return records

def h_get_yearly_records(CustomModel, year=None):
    if year is None:
        year = datetime.now().year

    monthly_totals = []
    for month in range(1, 13):
        total = h_get_monthly_records(CustomModel, year, month)
        monthly_totals.append(total)

    return monthly_totals

