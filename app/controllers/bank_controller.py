from flask import request

from app.models.bank import Bank
from app.extensions import db

def create_bank():
    if request.method == 'POST':
        name = request.form['name']

        bank = Bank(name=name)
        bank.save()

        data = {
            'id': bank.id,
            'name': bank.name,
            'created_at': bank.created_at
        }

        return data
    
def update_bank(bank):
    if request.method == 'POST':
        bank.name = request.form['name']

        db.session.commit()

def delete_bank(bank):
    if request.method == 'POST':
        db.session.delete(bank)
        db.session.commit()