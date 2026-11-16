"""Business rules for banks."""
from app.extensions import db
from app.models.bank import Bank
from app.exceptions.records import BankInUse
from app.services import money
from app.utils.transactions import atomic


def list_banks():
    return Bank.query.all()


def create_bank(*, name):
    with atomic():
        bank = Bank(name=name)
        db.session.add(bank)
    return bank


def update_bank(bank_id, *, name):
    with atomic():
        bank = money.get_record(Bank, bank_id, 'Bank')
        bank.name = name
    return bank


def delete_bank(bank_id):
    with atomic():
        bank = money.get_record(Bank, bank_id, 'Bank')
        if bank.bank_accounts or bank.credit_cards:
            raise BankInUse('This bank still has bank accounts or credit cards.')
        db.session.delete(bank)
