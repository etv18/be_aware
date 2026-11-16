"""Safety net for incomes, withdrawals and deposits.

These are the three "plain" money movements between cash and a bank account:
    income      -> money comes in (cash or bank account)
    withdrawal  -> bank account -> cash
    deposit     -> cash -> bank account

Every test goes through the HTTP routes with the same form fields the frontend sends.
"""
from decimal import Decimal

import pytest

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.deposit import Deposit
from app.models.income import Income
from app.models.withdrawal import Withdrawal


def form(amount, account=None, description='Test', created_at='2026-10-15T12:30', cash=False):
    """The JSON body of an income, withdrawal or deposit form."""
    return {
        'amount': str(amount),
        'description': description,
        'created_at': created_at,
        'bank_account_id': account.id if account else None,
        'is_cash': cash,
    }


def post(client, path, **kwargs):
    return client.post(path, json=form(**kwargs))


def put(client, path, **kwargs):
    return client.put(path, json=form(**kwargs))


def delete(client, path):
    return client.delete(path)


def balance(db, account):
    db.session.expire_all()
    return account.amount_available


def cash_total(db):
    return db.session.query(db.func.sum(CashLedger.amount)).scalar() or Decimal('0')


def put_cash_in_wallet(client, amount):
    """An income paid in cash, so deposits have cash to move."""
    assert post(client, '/api/incomes', amount=amount, cash=True).status_code == 201


# ================================================================ incomes

def test_income_to_bank_account_adds_money_and_writes_ledger(client, db, data):
    response = post(client, '/api/incomes', amount='200', account=data['account'])

    assert response.status_code == 201
    income = Income.query.one()
    assert income.code.startswith('INC')
    assert income.bank_account_id == data['account'].id
    assert balance(db, data['account']) == Decimal('1200.00')

    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('200.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('1200.00')
    assert CashLedger.query.count() == 0


def test_cash_income_writes_a_positive_cash_ledger(client, db, data):
    response = post(client, '/api/incomes', amount='75.50', cash=True)

    assert response.status_code == 201
    income = Income.query.one()
    assert income.is_cash is True and income.bank_account_id is None
    assert CashLedger.query.one().amount == Decimal('75.50')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_income_keeps_the_date_it_was_given(client):
    post(client, '/api/incomes', amount='10', cash=True, created_at='2026-09-03T08:15')

    created = Income.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_income_without_a_date_uses_now(client, data):
    response = client.post('/api/incomes', json={
        'amount': '10', 'description': 'x', 'is_cash': False, 'bank_account_id': data['account'].id})

    assert response.status_code == 201
    assert Income.query.one().created_at is not None


def test_income_rejects_bad_amounts_and_missing_account(client, db, data):
    for amount in ('0', '-5', 'abc'):
        assert post(client, '/api/incomes', amount=amount, account=data['account']).status_code in (400, 422), amount

    assert post(client, '/api/incomes', amount='10').status_code == 400  # no account and not cash

    assert Income.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_income_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(_boom))

    response = post(client, '/api/incomes', amount='200', account=data['account'])

    assert response.status_code == 500
    assert Income.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_income_update_amount_adjusts_balance_and_ledger(client, db, data):
    post(client, '/api/incomes', amount='200', account=data['account'])
    income_id = Income.query.one().id

    response = put(client, f'/api/incomes/{income_id}', amount='50', account=data['account'])

    assert response.status_code == 200
    assert Income.query.one().amount == Decimal('50.00')
    assert balance(db, data['account']) == Decimal('1050.00')
    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('50.00')
    assert ledger.after_update_balance == Decimal('1050.00')


def test_income_update_moves_it_to_another_account(client, db, data):
    post(client, '/api/incomes', amount='200', account=data['account'])
    income_id = Income.query.one().id

    put(client, f'/api/incomes/{income_id}', amount='200', account=data['account2'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('700.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_income_update_bank_to_cash_and_back(client, db, data):
    post(client, '/api/incomes', amount='200', account=data['account'])
    income_id = Income.query.one().id

    put(client, f'/api/incomes/{income_id}', amount='200', cash=True)

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.one().amount == Decimal('200.00')

    put(client, f'/api/incomes/{income_id}', amount='200', account=data['account'])

    assert balance(db, data['account']) == Decimal('1200.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 1


def test_income_update_of_a_missing_record_is_404(client):
    response = put(client, '/api/incomes/999', amount='10', cash=True)

    assert response.status_code == 404


def test_income_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    post(client, '/api/incomes', amount='200', account=data['account'])
    income_id = Income.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'update', staticmethod(_boom))

    response = put(client, f'/api/incomes/{income_id}', amount='500', account=data['account'])

    assert response.status_code == 500
    assert Income.query.one().amount == Decimal('200.00')
    assert balance(db, data['account']) == Decimal('1200.00')


def test_income_delete_takes_the_money_back_and_removes_ledgers(client, db, data):
    post(client, '/api/incomes', amount='200', account=data['account'])
    post(client, '/api/incomes', amount='30', cash=True)
    bank_income, cash_income = Income.query.order_by(Income.id).all()

    assert delete(client, f'/api/incomes/{bank_income.id}').status_code == 204
    assert delete(client, f'/api/incomes/{cash_income.id}').status_code == 204

    assert Income.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.count() == 0


def test_income_delete_of_a_missing_record_is_404_and_changes_nothing(client, db, data):
    response = delete(client, '/api/incomes/999')

    assert response.status_code == 404
    assert balance(db, data['account']) == Decimal('1000.00')


def test_income_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    post(client, '/api/incomes', amount='200', account=data['account'])
    income_id = Income.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(_boom))

    response = delete(client, f'/api/incomes/{income_id}')

    assert response.status_code == 500
    assert Income.query.count() == 1
    assert balance(db, data['account']) == Decimal('1200.00')


def test_income_filters(client, data):
    post(client, '/api/incomes', amount='100', account=data['account'], description='Salary', created_at='2026-10-15T12:00')
    post(client, '/api/incomes', amount='20', cash=True, description='Gift', created_at='2026-09-01T12:00')

    by_time = client.get('/api/incomes', query_string={'start': '2026-10-01', 'end': '2026-10-31'}).get_json()
    assert [i['description'] for i in by_time['data']] == ['Salary']
    assert by_time['meta']['total'] == '100.00'

    by_field = client.get('/api/incomes', query_string={'q': 'checking'}).get_json()
    assert [i['description'] for i in by_field['data']] == ['Salary']

    yes = client.get('/api/incomes', query_string={'q': 'yes'}).get_json()
    assert [i['description'] for i in yes['data']] == ['Gift']

    both = client.get('/api/incomes', query_string={'q': 'a', 'start': '2026-10-01', 'end': '2026-10-31'}).get_json()
    assert [i['description'] for i in both['data']] == ['Salary']

    assert client.get('/api/incomes', query_string={'start': '2026-10-01'}).status_code == 422  # both dates or none


def test_income_index_page_renders(client, data):
    post(client, '/api/incomes', amount='100', account=data['account'])

    assert client.get('/incomes').status_code == 200


# ================================================================ withdrawals

def test_withdrawal_takes_from_the_account_and_adds_cash(client, db, data):
    response = post(client, '/api/withdrawals', amount='300', account=data['account'])

    assert response.status_code == 201
    withdrawal = Withdrawal.query.one()
    assert withdrawal.code.startswith('WDR')
    assert balance(db, data['account']) == Decimal('700.00')

    assert CashLedger.query.one().amount == Decimal('300.00')
    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('-300.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('700.00')


def test_withdrawal_with_more_than_the_available_money_changes_nothing(client, db, data):
    response = post(client, '/api/withdrawals', amount='5000', account=data['account'])

    assert response.status_code == 400
    assert 'Insufficient' in response.get_json()['error']['message']
    assert Withdrawal.query.count() == 0
    assert CashLedger.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_withdrawal_rejects_bad_amounts_and_missing_account(client, db, data):
    for amount in ('0', '-5', 'abc'):
        assert post(client, '/api/withdrawals', amount=amount, account=data['account']).status_code in (400, 422), amount

    assert post(client, '/api/withdrawals', amount='10').status_code == 422

    assert Withdrawal.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_withdrawal_keeps_the_date_it_was_given(client, data):
    post(client, '/api/withdrawals', amount='10', account=data['account'], created_at='2026-09-03T08:15')

    created = Withdrawal.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_withdrawal_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    monkeypatch.setattr(CashLedger, 'create', staticmethod(_boom))

    response = post(client, '/api/withdrawals', amount='300', account=data['account'])

    assert response.status_code == 500
    assert Withdrawal.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_withdrawal_update_amount_on_the_same_account(client, db, data):
    post(client, '/api/withdrawals', amount='300', account=data['account'])
    withdrawal_id = Withdrawal.query.one().id

    response = put(client, f'/api/withdrawals/{withdrawal_id}', amount='100', account=data['account'])

    assert response.status_code == 200
    assert balance(db, data['account']) == Decimal('900.00')
    assert CashLedger.query.one().amount == Decimal('100.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('-100.00')


def test_withdrawal_update_to_another_account(client, db, data):
    post(client, '/api/withdrawals', amount='300', account=data['account'])
    withdrawal_id = Withdrawal.query.one().id

    put(client, f'/api/withdrawals/{withdrawal_id}', amount='300', account=data['account2'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('200.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_withdrawal_update_with_more_than_the_available_money_changes_nothing(client, db, data):
    post(client, '/api/withdrawals', amount='300', account=data['account'])
    withdrawal_id = Withdrawal.query.one().id

    response = put(client, f'/api/withdrawals/{withdrawal_id}', amount='900', account=data['account2'])

    assert response.status_code == 400
    assert Withdrawal.query.one().amount == Decimal('300.00')
    assert balance(db, data['account']) == Decimal('700.00')
    assert balance(db, data['account2']) == Decimal('500.00')


def test_withdrawal_update_of_a_missing_record_is_an_error(client):
    response = put(client, '/api/withdrawals/999', amount='10', account=None)

    assert response.status_code in (400, 404, 422)


def test_withdrawal_delete_gives_the_money_back(client, db, data):
    post(client, '/api/withdrawals', amount='300', account=data['account'])
    withdrawal_id = Withdrawal.query.one().id

    response = delete(client, f'/api/withdrawals/{withdrawal_id}')

    assert response.status_code == 204
    assert Withdrawal.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 0


def test_withdrawal_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    post(client, '/api/withdrawals', amount='300', account=data['account'])
    withdrawal_id = Withdrawal.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(_boom))

    response = delete(client, f'/api/withdrawals/{withdrawal_id}')

    assert response.status_code == 500
    assert Withdrawal.query.count() == 1
    assert balance(db, data['account']) == Decimal('700.00')


def test_withdrawal_delete_of_a_missing_record_changes_nothing(client, db, data):
    delete(client, '/api/withdrawals/999')

    assert balance(db, data['account']) == Decimal('1000.00')


def test_withdrawal_filters(client, data):
    post(client, '/api/withdrawals', amount='100', account=data['account'], description='ATM', created_at='2026-10-15T12:00')
    post(client, '/api/withdrawals', amount='20', account=data['account2'], description='Old', created_at='2026-09-01T12:00')

    by_time = client.get('/api/withdrawals', query_string={'start': '2026-10-01', 'end': '2026-10-31'}).get_json()
    assert [w['description'] for w in by_time['data']] == ['ATM']
    assert by_time['meta']['total'] == '100.00'

    by_field = client.get('/api/withdrawals', query_string={'q': 'savings'}).get_json()
    assert [w['description'] for w in by_field['data']] == ['Old']

    both = client.get('/api/withdrawals', query_string={'q': 'atm', 'start': '2026-10-01', 'end': '2026-10-31'}).get_json()
    assert [w['description'] for w in both['data']] == ['ATM']

    assert client.get('/api/withdrawals', query_string={'end': '2026-10-31'}).status_code == 422


def test_withdrawal_index_page_renders(client, data):
    post(client, '/api/withdrawals', amount='100', account=data['account'])

    assert client.get('/withdrawals').status_code == 200


# ================================================================ deposits

def test_deposit_moves_cash_into_the_account(client, db, data):
    put_cash_in_wallet(client, '500')

    response = post(client, '/api/deposits', amount='200', account=data['account'])

    assert response.status_code == 201
    deposit = Deposit.query.one()
    assert deposit.code.startswith('DPT')
    assert balance(db, data['account']) == Decimal('1200.00')
    assert cash_total(db) == Decimal('300.00')

    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('200.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('1200.00')


def test_deposit_needs_enough_cash(client, db, data):
    put_cash_in_wallet(client, '50')

    response = post(client, '/api/deposits', amount='200', account=data['account'])

    assert response.status_code == 400
    assert 'cash' in response.get_json()['error']['message'].lower()
    assert Deposit.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_deposit_rejects_bad_amounts_and_missing_account(client, db, data):
    put_cash_in_wallet(client, '500')

    for amount in ('0', '-5', 'abc'):
        assert post(client, '/api/deposits', amount=amount, account=data['account']).status_code in (400, 422), amount
    assert post(client, '/api/deposits', amount='10').status_code == 422

    assert Deposit.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_deposit_keeps_the_date_it_was_given(client, data):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='10', account=data['account'], created_at='2026-09-03T08:15')

    created = Deposit.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_deposit_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    put_cash_in_wallet(client, '500')
    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(_boom))

    response = post(client, '/api/deposits', amount='200', account=data['account'])

    assert response.status_code == 500
    assert Deposit.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert cash_total(db) == Decimal('500.00')


def test_deposit_update_amount_on_the_same_account(client, db, data):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='200', account=data['account'])
    deposit_id = Deposit.query.one().id

    response = put(client, f'/api/deposits/{deposit_id}', amount='100', account=data['account'])

    assert response.status_code == 200
    assert balance(db, data['account']) == Decimal('1100.00')
    assert cash_total(db) == Decimal('400.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('100.00')


def test_deposit_update_to_another_account(client, db, data):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='200', account=data['account'])
    deposit_id = Deposit.query.one().id

    put(client, f'/api/deposits/{deposit_id}', amount='200', account=data['account2'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('700.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_deposit_update_of_a_missing_record_is_an_error(client):
    response = put(client, '/api/deposits/999', amount='10', account=None)

    assert response.status_code in (400, 404, 422)


def test_deposit_delete_takes_the_money_back_out_of_the_account(client, db, data):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='200', account=data['account'])
    deposit_id = Deposit.query.one().id

    response = delete(client, f'/api/deposits/{deposit_id}')

    assert response.status_code == 204
    assert Deposit.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert cash_total(db) == Decimal('500.00')
    assert BankAccountTransactionsLedger.query.count() == 0


def test_deposit_delete_is_refused_when_the_account_no_longer_has_the_money(client, db, data):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='200', account=data['account'])
    deposit_id = Deposit.query.one().id
    post(client, '/api/withdrawals', amount='1150', account=data['account'])  # leaves 50

    response = delete(client, f'/api/deposits/{deposit_id}')

    assert response.status_code == 400
    assert Deposit.query.count() == 1
    assert balance(db, data['account']) == Decimal('50.00')


def test_deposit_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='200', account=data['account'])
    deposit_id = Deposit.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(_boom))

    response = delete(client, f'/api/deposits/{deposit_id}')

    assert response.status_code == 500
    assert Deposit.query.count() == 1
    assert balance(db, data['account']) == Decimal('1200.00')


def test_deposit_filters(client, data):
    put_cash_in_wallet(client, '500')
    post(client, '/api/deposits', amount='100', account=data['account'], description='Pay in', created_at='2026-10-15T12:00')
    post(client, '/api/deposits', amount='20', account=data['account2'], description='Old', created_at='2026-09-01T12:00')

    by_time = client.get('/api/deposits', query_string={'start': '2026-10-01', 'end': '2026-10-31'}).get_json()
    assert [d['description'] for d in by_time['data']] == ['Pay in']

    by_field = client.get('/api/deposits', query_string={'q': 'savings'}).get_json()
    assert [d['description'] for d in by_field['data']] == ['Old']

    both = client.get('/api/deposits', query_string={'q': 'pay', 'start': '2026-10-01', 'end': '2026-10-31'}).get_json()
    assert [d['description'] for d in both['data']] == ['Pay in']

    assert client.get('/api/deposits', query_string={'start': '2026-10-01'}).status_code == 422


def test_deposit_index_page_renders(client, data):
    assert client.get('/deposits').status_code == 200


def _boom(*args, **kwargs):
    raise RuntimeError('ledger is down')
