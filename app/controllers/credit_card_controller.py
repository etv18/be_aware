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