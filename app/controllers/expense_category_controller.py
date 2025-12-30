from flask import request, jsonify
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal 
from datetime import datetime
import traceback

from app.extensions import db
from app.models.expense_category import ExpenseCategory
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.models.expense import Expense
from app.utils.numeric_casting import format_amount, total_amount, is_decimal_type
from app.utils.parse_structures import get_data_as_dictionary

def create_expense_category():
    try:
        name = request.form.get('name')
        limit = Decimal(request.form.get('limit')) if is_decimal_type(request.form.get('limit')) else -1
        
        validName(name)
        if(limit < 0): raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')

        expense_category = ExpenseCategory(
            name=name.upper(),
            limit=limit
        )

        db.session.add(expense_category)
        db.session.commit()

        return jsonify({'message': 'Expense category created successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

def update_expense_category(expense_category):
    try:
        name = request.form.get('name')
        limit = Decimal(request.form.get('limit')) if is_decimal_type(request.form.get('limit')) else -1
        
        validName(name)
        if(limit < 0): raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')

        expense_category.name = name
        expense_category.limit = limit

        db.session.commit()

        return jsonify({'message': 'Expense category updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

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
    
def associated_records_in_json(id):
    try:
        category = ExpenseCategory.query.get(id)
        if not category: 
            return jsonify({'error': 'Expense category not found'}), 404

        associations = [
            category.expenses,
        ]
        data = {}
        for a in associations:
            if a:
                table_name = a[0].__class__.__tablename__; '''access the first element to get its table name'''
                data[table_name] = get_data_as_dictionary(a); '''set the table name as the key and use the function to  get all elements of the list in dictionary format'''
        
        return jsonify({'records': data}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

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

def validName(name: str):
    if not name or len(name) < 4:
        raise Exception('Category Name must have for characters or more')

