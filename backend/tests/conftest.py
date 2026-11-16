import warnings
from decimal import Decimal

import pytest
from sqlalchemy.exc import SAWarning

from app import create_app
from app.extensions import db as _db
from app.models.bank import Bank
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.models.expense_category import ExpenseCategory
from app.models.user import User

# SQLite stores Numeric as float, SQLAlchemy warns about it on every query. Money is rounded
# to 2 decimals on the way back out, so the warning is noise for these tests.
warnings.filterwarnings('ignore', message='.*does \\*not\\* support Decimal objects natively.*', category=SAWarning)


@pytest.fixture()
def app():
    app = create_app('testing')

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def data(db):
    """A bank with two accounts, two credit cards and two categories, plus the logged in user."""
    bank = Bank(name='Test Bank')
    db.session.add(bank)
    db.session.flush()

    records = {
        'user': User(username='tester', password=b'not-used-in-tests'),
        'bank': bank,
        'account': BankAccount(nick_name='Checking', amount_available=Decimal('1000.00'), bank_id=bank.id),
        'account2': BankAccount(nick_name='Savings', amount_available=Decimal('500.00'), bank_id=bank.id),
        'card': CreditCard(nick_name='Visa', amount_available=Decimal('800.00'), limit=Decimal('800.00'), bank_id=bank.id),
        'card2': CreditCard(nick_name='Master', amount_available=Decimal('300.00'), limit=Decimal('300.00'), bank_id=bank.id),
        'food': ExpenseCategory(name='FOOD', limit=Decimal('300.00')),
        'fuel': ExpenseCategory(name='FUEL', limit=Decimal('100.00')),
    }
    db.session.add_all(records.values())
    db.session.commit()

    return records


@pytest.fixture()
def client(app, data):
    client = app.test_client()

    with client.session_transaction() as session:
        session['_user_id'] = str(data['user'].id)
        session['_fresh'] = True

    return client
