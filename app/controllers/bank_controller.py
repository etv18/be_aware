from app.models.bank import Bank
from flask import request

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
