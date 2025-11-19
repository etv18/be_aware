from flask import request

from sqlalchemy import extract, func

from decimal import Decimal
from datetime import datetime

from app.extensions import db
from app.models.expense import Expense
from app.models.income import Income

def get_income_and_expense_data():
    try:
        expenses = h_get_monthly_records(Expense)
        incomes = h_get_monthly_records(Income)
    except Exception as e:
        print(e)
        raise e
    
    return {'incomes': incomes, 'expenses': expenses}

def h_get_monthly_records(CustomModel):
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    records = CustomModel.query.filter(
        extract('year', CustomModel.created_at) == current_year,
        extract('month', CustomModel.created_at) == current_month
    ).with_entities(func.sum(CustomModel.amount)).scalar() or Decimal(0.00)
     
 
    return records
