from flask import request

from decimal import Decimal

from app.extensions import db
from app.models.expense import Expense
from app.models.income import Income

def get_income_and_expense_data():
    try:
        expenses = Expense.query.with_entities(Expense.amount).all()
        incomes = Income.query.with_entities(Income.amount).all()
        '''
            output incomes/expenses = [(10,), (7424,), (100,), (4733,), ...]

            they return as sqlalchemy objects which are a list of tuples
        '''
        ex_total = 0.0
        for e in expenses:
            ex_total += float(e[0])

        in_total = 0.0
        for i in incomes:
            in_total += float(i[0])

    except Exception as e:
        print(e)
        raise e
    
    return {'incomes': in_total, 'expenses': ex_total}
