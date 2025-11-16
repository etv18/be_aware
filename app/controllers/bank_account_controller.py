from flask import request, jsonify

from app.models.bank_account import BankAccount
from app.models.expense import Expense
from app.exceptions.bankProductsException import BankAccountDoesNotExists
from app.extensions import db

def create_bank_account():
    if request.method == 'POST':
        nick_name = request.form['nick-name']
        amount_available = request.form['amount-available']
        account_number = request.form['account-number']
        bank_id = int(request.form['select-banks'])

        bank_account = BankAccount(
            nick_name=nick_name,
            amount_available=amount_available,
            account_number=account_number,
            bank_id=bank_id
        )

        db.session.add(bank_account)
        db.session.commit()

def update_bank_account(bank_account):
    if request.method == 'POST':
        bank_account.nick_name = request.form['e-nick-name'];
        bank_account.account_number = request.form['e-account-number'];
        bank_account.amount_available = request.form['e-amount-available'];

        bank_id = request.form['e-select-banks'];
        bank_account.bank_id = int(bank_id)

        db.session.commit()

def delete_bank_account(bank_account):
    if request.method == 'POST':
        db.session.delete(bank_account)
        db.session.commit()

def get_associated_records(id):
    data = {}
    try:    
        expenses = Expense.query.filter(Expense.bank_account_id == id).all()
        data = {
            'expenses': expenses,
        }
    except BankAccountDoesNotExists as e:
        raise BankAccountDoesNotExists('Bank account does not exists.')
    except Exception as e:
        raise e
    return data