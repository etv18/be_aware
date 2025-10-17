from flask import request

from app.models.bank import Bank
from app.extensions import db

def create_bank():
    if request.method == 'POST':
        name = request.form['name']

        bank = Bank(name=name)

        db.session.add(bank)
        db.session.commit()
    
def update_bank(bank):
    if request.method == 'POST':
        bank.name = request.form['name']

        db.session.commit()

def delete_bank(bank):
    if request.method == 'POST':
        db.session.delete(bank)
        db.session.commit()