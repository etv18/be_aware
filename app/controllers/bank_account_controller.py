from flask import request

from app.models.bank_account import BankAccount
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