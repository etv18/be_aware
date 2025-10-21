from flask import request

from app.models.credit_card import CreditCard
from app.extensions import db

def create_credit_card():
    if request.method == 'POST':
        nick_name = request.form['nick-name']
        amount_available = request.form['amount-available']
        limit = request.form['limit']
        bank_id = request.form['select-banks']

        credit_card = CreditCard(
            nick_name=nick_name,
            amount_available=amount_available,
            limit=limit,
            bank_id=bank_id
        )

        db.session.add(credit_card)
        db.session.commit()

def update_credit_card(credit_card):
    if request.method == 'POST':
        credit_card.nick_name = request.form['e-nick-name']
        credit_card.limit = request.form['e-limit']
        credit_card.amount_available = request.form['e-amount-available']
        
        bank_id = request.form['e-select-banks']
        credit_card.bank_id = int(bank_id)

        db.session.commit()

def delete_credit_card(credit_card):
    if request.method == 'POST':
        db.session.delete(credit_card)
        db.session.commit()