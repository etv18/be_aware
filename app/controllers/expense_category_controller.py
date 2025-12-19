from flask import request, jsonify
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal 
from datetime import datetime

from app.extensions import db
from app.models.expense_category import ExpenseCategory
from app.models.expense import Expense
from app.utils.numeric_casting import format_amount, total_amount

def create_expense_category():
    if request.method == 'POST':
        name = request.form.get('name')
        limit = request.form.get('limit')
        
        expense_category = ExpenseCategory(
            name=name,
            limit=limit
        )

        db.session.add(expense_category)
        db.session.commit()

def update_expense_category(expense_category):
    if request.method == 'POST':
        expense_category.name = request.form.get('name')
        expense_category.limit = request.form.get('limit')

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
        data = {
            'category': category,
            'format_amount': format_amount, #function
            'total_amount': total_amount, #function
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




