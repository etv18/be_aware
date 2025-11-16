from flask import request
from sqlalchemy import func 

from decimal import Decimal 

from app.extensions import db
from app.models.expense_category import ExpenseCategory
from app.models.expense import Expense

def create_expense_category():
    if request.method == 'POST':
        name = request.form['name']

        expense_category = ExpenseCategory(name=name)

        db.session.add(expense_category)
        db.session.commit()

def update_expense_category(expense_category):
    if request.method == 'POST':
        expense_category.name = request.form['name']

        db.session.commit()

def delete_expense_category(expense_category):
    if request.method == 'POST':
        db.session.delete(expense_category)
        db.session.commit()

def get_associated_records(category_id):
    data = {}
    try:
        category = ExpenseCategory.query.get(category_id)
        query = Expense.query.filter(Expense.expense_category_id == category_id)
        expenses = query.order_by(Expense.created_at.desc()).all()
        count_expenses = query.count()
        total_expenses = query.with_entities(func.sum(Expense.amount)).scalar() or Decimal(0.00)
        data = {
            'expenses': expenses,
            'count_expenses': count_expenses,
            'total_expenses': total_expenses,
            'category': category,
        }
    except Exception as e:
        raise e
    return data


