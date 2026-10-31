"""Safety net for the expense money flows.

Every test talks to the app the way the browser does (JSON to /expenses), so the same
tests keep working while the code behind the routes is being refactored.
"""
from decimal import Decimal

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.models.expense import Expense

from tests.helpers import delete_expense, post_expense, put_expense


def balances(db, data):
    db.session.expire_all()
    return {name: getattr(data[name], 'amount_available') for name in ('account', 'account2', 'card', 'card2')}


def only_expense():
    return Expense.query.one()


# ---------------------------------------------------------------- create

def test_create_cash_expense_writes_cash_ledger_and_keeps_balances(client, db, data):
    response = post_expense(client, amount='25.50', category=data['food'], cash=True)

    assert response.status_code == 201
    expense = only_expense()
    assert expense.is_cash is True
    assert expense.amount == Decimal('25.50')
    assert expense.code.startswith('EXP_')
    assert expense.bank_account_id is None and expense.credit_card_id is None

    ledger = CashLedger.query.one()
    assert ledger.amount == Decimal('-25.50')
    assert ledger.reference_code == expense.code
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.count() == 0

    assert balances(db, data) == {
        'account': Decimal('1000.00'), 'account2': Decimal('500.00'),
        'card': Decimal('800.00'), 'card2': Decimal('300.00'),
    }


def test_create_bank_account_expense_takes_money_and_writes_ledger(client, db, data):
    response = post_expense(client, amount='150.50', category=data['food'], account=data['account'])

    assert response.status_code == 201
    expense = only_expense()
    assert expense.is_cash is False
    assert expense.bank_account_id == data['account'].id

    assert balances(db, data)['account'] == Decimal('849.50')

    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('-150.50')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('849.50')
    assert ledger.bank_account_id == data['account'].id
    assert ledger.reference_code == expense.code
    assert CashLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.count() == 0


def test_create_credit_card_expense_takes_money_and_writes_ledger(client, db, data):
    response = post_expense(client, amount='200', category=data['fuel'], card=data['card'])

    assert response.status_code == 201
    assert balances(db, data)['card'] == Decimal('600.00')

    ledger = CreditCardTransactionsLedger.query.one()
    assert ledger.amount == Decimal('-200.00')
    assert ledger.before_update_balance == Decimal('800.00')
    assert ledger.after_update_balance == Decimal('600.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.count() == 0


def test_create_without_a_date_uses_the_current_time(client, data):
    form_response = client.post('/api/expenses', json={
        'amount': '10', 'is_cash': False, 'expense_category_id': data['food'].id, 'description': 'No date',
        'bank_account_id': data['account'].id,
    })

    assert form_response.status_code == 201
    assert only_expense().created_at is not None


def test_create_with_more_than_the_available_money_changes_nothing(client, db, data):
    response = post_expense(client, amount='400', category=data['food'], card=data['card2'])

    assert response.status_code == 400
    assert 'Insufficient' in response.get_json()['error']['message']
    assert Expense.query.count() == 0
    assert CreditCardTransactionsLedger.query.count() == 0
    assert balances(db, data)['card2'] == Decimal('300.00')


def test_create_rejects_zero_and_negative_amounts(client, db, data):
    for amount in ('0', '-5', 'abc'):
        response = post_expense(client, amount=amount, category=data['food'], cash=True)
        assert response.status_code in (400, 422), amount

    assert Expense.query.count() == 0


def test_create_without_cash_or_bank_product_is_rejected(client, data):
    response = post_expense(client, amount='10', category=data['food'])

    assert response.status_code == 400
    assert Expense.query.count() == 0


def test_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    def broken_ledger(*args, **kwargs):
        raise RuntimeError('ledger is down')

    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(broken_ledger))

    response = post_expense(client, amount='100', category=data['food'], account=data['account'])

    assert response.status_code == 500
    assert Expense.query.count() == 0
    assert balances(db, data)['account'] == Decimal('1000.00')


# ---------------------------------------------------------------- update

def test_update_amount_on_the_same_account_adjusts_balance_and_ledger(client, db, data):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='250', category=data['food'], account=data['account'])

    assert response.status_code == 200
    assert only_expense().amount == Decimal('250.00')
    assert balances(db, data)['account'] == Decimal('750.00')

    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('-250.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('750.00')


def test_update_moves_the_charge_to_another_bank_account(client, db, data):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='100', category=data['food'], account=data['account2'])

    assert response.status_code == 200
    result = balances(db, data)
    assert result['account'] == Decimal('1000.00')
    assert result['account2'] == Decimal('400.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_update_from_bank_account_to_credit_card(client, db, data):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='100', category=data['food'], card=data['card'])

    assert response.status_code == 200
    result = balances(db, data)
    assert result['account'] == Decimal('1000.00')
    assert result['card'] == Decimal('700.00')

    expense = only_expense()
    assert expense.bank_account_id is None
    assert expense.credit_card_id == data['card'].id
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.one().reference_code == expense.code


def test_update_from_credit_card_to_bank_account(client, db, data):
    post_expense(client, amount='100', category=data['food'], card=data['card'])
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='100', category=data['food'], account=data['account'])

    assert response.status_code == 200
    result = balances(db, data)
    assert result['card'] == Decimal('800.00')
    assert result['account'] == Decimal('900.00')
    assert CreditCardTransactionsLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 1


def test_update_to_cash_gives_the_money_back_and_moves_the_ledger(client, db, data):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='100', category=data['food'], cash=True)

    assert response.status_code == 200
    assert balances(db, data)['account'] == Decimal('1000.00')

    expense = only_expense()
    assert expense.is_cash is True
    assert expense.bank_account_id is None
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.one().amount == Decimal('-100.00')


def test_update_from_cash_to_bank_account_takes_the_money(client, db, data):
    post_expense(client, amount='100', category=data['food'], cash=True)
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='100', category=data['food'], account=data['account'])

    assert response.status_code == 200
    assert balances(db, data)['account'] == Decimal('900.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 1


def test_update_with_more_than_the_available_money_changes_nothing(client, db, data):
    post_expense(client, amount='900', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    response = put_expense(client, expense_id, amount='1200', category=data['food'], account=data['account'])

    assert response.status_code == 400
    assert only_expense().amount == Decimal('900.00')
    assert balances(db, data)['account'] == Decimal('100.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('-900.00')


def test_update_can_change_category_description_and_date(client, data):
    post_expense(client, amount='20', category=data['food'], cash=True)
    expense_id = only_expense().id

    response = put_expense(
        client, expense_id, amount='20', category=data['fuel'], cash=True,
        description='Gas', created_at='2026-09-03 08:15',
    )

    assert response.status_code == 200
    expense = only_expense()
    assert expense.expense_category_id == data['fuel'].id
    assert expense.description == 'Gas'
    assert (expense.created_at.year, expense.created_at.month, expense.created_at.day) == (2026, 9, 3)


def test_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    def broken_ledger(*args, **kwargs):
        raise RuntimeError('ledger is down')

    monkeypatch.setattr(BankAccountTransactionsLedger, 'update', staticmethod(broken_ledger))

    response = put_expense(client, expense_id, amount='300', category=data['food'], account=data['account'])

    assert response.status_code == 500
    assert only_expense().amount == Decimal('100.00')
    assert balances(db, data)['account'] == Decimal('900.00')


def test_update_of_a_missing_expense_returns_404(client, db, data):
    response = put_expense(client, 9999, amount='10', category=data['food'], cash=True)

    assert response.status_code == 404
    assert 'not found' in response.get_json()['error']['message'].lower()


# ---------------------------------------------------------------- delete

def test_delete_bank_account_expense_refunds_and_removes_ledger(client, db, data):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    response = delete_expense(client, expense_id)

    assert response.status_code == 204
    assert Expense.query.count() == 0
    assert balances(db, data)['account'] == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0


def test_delete_credit_card_expense_refunds_and_removes_ledger(client, db, data):
    post_expense(client, amount='100', category=data['food'], card=data['card'])
    expense_id = only_expense().id

    response = delete_expense(client, expense_id)

    assert response.status_code == 204
    assert Expense.query.count() == 0
    assert balances(db, data)['card'] == Decimal('800.00')
    assert CreditCardTransactionsLedger.query.count() == 0


def test_delete_cash_expense_removes_cash_ledger(client, data):
    post_expense(client, amount='100', category=data['food'], cash=True)
    expense_id = only_expense().id

    response = delete_expense(client, expense_id)

    assert response.status_code == 204
    assert Expense.query.count() == 0
    assert CashLedger.query.count() == 0


def test_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    post_expense(client, amount='100', category=data['food'], account=data['account'])
    expense_id = only_expense().id

    def broken_ledger(*args, **kwargs):
        raise RuntimeError('ledger is down')

    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(broken_ledger))

    response = delete_expense(client, expense_id)

    assert response.status_code == 500
    assert Expense.query.count() == 1
    assert balances(db, data)['account'] == Decimal('900.00')


def test_delete_of_a_missing_expense_changes_no_balance(client, db, data):
    delete_expense(client, 9999)

    assert balances(db, data)['account'] == Decimal('1000.00')
