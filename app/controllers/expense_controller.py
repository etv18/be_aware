from flask import request

from app.extensions import db
from app.models.expense import Expense

def create_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        is_cash = request.form.get('is-cash') == 'on'
        expense_category_id = int(request.form['select-expense-category'])
        credit_card_id = None
        bank_account_id = None
        '''
            this conditional will save either a credit_card_id or a bank_account_id
            only if you marked the expense as it wasn't made with cash, in other words...
            
            the code inside the if statement will be executed ONLY if you on the frontend 
            turn off the switcher which determines if you did or didn't use cash on the 
            transaction you just created.
        '''
        if not is_cash:
            selected_credit_card = request.form.get('select-credit-card')
            selected_bank_account = request.form.get('select-bank-account')

            if selected_credit_card and selected_credit_card != 'none':
                credit_card_id = int(request.form['select-credit-card'])

            if selected_bank_account and selected_bank_account != 'none':
                bank_account_id = int(request.form['select-bank-account'])

        expense = Expense(
            amount=amount,
            is_cash=is_cash,
            expense_category_id=expense_category_id,
            credit_card_id=credit_card_id,
            bank_account_id=bank_account_id
        )

        db.session.add(expense)
        db.session.commit()

def update_expense(expense):
    if request.method == 'POST':
        amount = request.form['amount']
        is_cash = request.form.get('is-cash') == 'on'
        expense_category_id = int(request.form['select-expense-category'])
        credit_card_id = None
        bank_account_id = None

        '''
        if the expense you are updating, you edit it as it wasnt made with
        cash then the program it'll save either the credit_card_id or 
        bank_account_id
        '''
        if not is_cash:
            selected_credit_card = request.form.get('select-credit-card')
            selected_bank_account = request.form.get('select-bank-account')

            if selected_credit_card and selected_credit_card != 'none':
                credit_card_id = int(request.form['select-credit-card'])

            if selected_bank_account and selected_bank_account != 'none':
                bank_account_id = int(request.form['select-bank-account'])

        expense.amount = amount
        expense.is_cash = is_cash
        expense.expense_category_id = expense_category_id
        expense.credit_card_id = credit_card_id
        expense.bank_account_id = bank_account_id

        db.session.commit()

def delete_expense(expense):
    if request.method == 'POST':
        db.session.delete(expense)
        db.session.commit()

