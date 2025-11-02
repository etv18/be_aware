from flask import request

from app.models.income import Income
from app.extensions import db

def create_income():
    if request.method == 'POST':
        amount = request.form['amount']
        is_cash = request.form.get('is-cash') == 'on'
        bank_account_id = None

        if not is_cash:
            bank_account_id = int(request.form.get('select-bank-account'))
            
        income = Income(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id
        )

        db.session.add(income)
        db.session.commit()

def update_income(income):
    if request.method == 'POST':
        income.amount = request.form['amount']
        income.is_cash = request.form.get('is-cash') == 'on'
        income.bank_account_id = None
        selected_bank_account = request.form.get('select-bank-account')

        if not income.is_cash and selected_bank_account != None:
            income.bank_account_id = int(selected_bank_account)
        
        db.session.commit()

            