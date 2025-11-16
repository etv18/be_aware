from flask import request

from app.extensions import db
from app.models.expense_category import ExpenseCategory

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
    pass
