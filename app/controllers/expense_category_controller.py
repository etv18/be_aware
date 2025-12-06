from flask import request, jsonify
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal 
from datetime import datetime

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
    try:
        db.session.delete(expense_category)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e

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

def get_monthly_data():
    now = datetime.now()
    data = {}
    try:
        category_names = ExpenseCategory.query.with_entities(ExpenseCategory.name).all()
        ids = ExpenseCategory.query.with_entities(ExpenseCategory.id).all()
        total_per_category = []

        category_names_list = []
        for item in category_names:
            category_names_list.append(item[0])

        ids_list = []
        for item in ids:
            ids_list.append(item[0])

        for category_id in ids_list:
            amount = (
                Expense.query
                .with_entities(func.sum(Expense.amount))
                .filter(Expense.expense_category_id == category_id)
                .filter(
                    extract('year', Expense.created_at) == now.year,
                    extract('month', Expense.created_at) == now.month
                )
                .scalar() or Decimal(0.00)
            )
            total_per_category.append(amount)
        data = {
            'names': category_names_list,
            'totals': total_per_category,
        }

        return data
    except Exception as e:
        return jsonify({'error': str(e)}), 400




