from decimal import Decimal

from app.models.bank_account import BankAccount

H = {}


def test_lists_and_error_format(client, db, data):
    r = client.get('/bank_accounts')
    assert r.status_code == 200
    assert [a['nick_name'] for a in r.get_json()['data']] == ['Checking', 'Savings']

    r = client.get('/expenses/999')
    assert r.status_code == 404
    assert r.get_json()['error']['code'] == 'not_found'


def test_expense_roundtrip(client, db, data):
    r = client.post('/expenses', json={
        'amount': '25.50', 'is_cash': False, 'expense_category_id': data['food'].id,
        'description': 'Lunch', 'bank_account_id': data['account'].id, 'created_at': '2026-10-15T12:30'})
    assert r.status_code == 201, r.get_json()
    body = r.get_json()['data']
    assert body['amount'] == '25.50' and body['created_at'] == '2026-10-15T12:30:00'
    assert body['bank_account_name'] == 'Checking' and body['expense_category_name'] == 'Food'

    r = client.get('/expenses?q=lunch')
    assert r.get_json()['meta']['count'] == 1 and r.get_json()['meta']['total'] == '25.50'

    r = client.put(f"/expenses/{body['id']}", json={
        'amount': '30', 'is_cash': True, 'expense_category_id': data['food'].id, 'description': 'Lunch'})
    assert r.status_code == 200 and r.get_json()['data']['amount'] == '30.00'
    assert db.session.get(BankAccount, data['account'].id).amount_available == Decimal('1000.00')

    assert client.delete(f"/expenses/{body['id']}").status_code == 204
    assert client.get(f"/expenses/{body['id']}").status_code == 404


def test_validation_and_business_errors(client, db, data):
    r = client.post('/expenses', json={'amount': 'abc', 'is_cash': True})
    assert r.status_code == 422
    err = r.get_json()['error']
    assert err['code'] == 'validation_error' and 'amount' in err['fields'] and 'description' in err['fields']

    r = client.post('/expenses', json={
        'amount': '5000', 'is_cash': False, 'expense_category_id': data['food'].id,
        'description': 'x', 'bank_account_id': data['account'].id})
    assert r.status_code == 400
    assert r.get_json()['error']['code'] == 'amount_greater_than_available_money'

    r = client.post('/expenses', data='nope', content_type='text/plain')
    assert r.status_code == 400


def test_everything_lists(client, db, data):
    for path in ('banks', 'bank_accounts', 'credit_cards', 'expense_categories', 'expenses', 'incomes', 'withdrawals',
                 'deposits', 'loans', 'debts', 'loan_payments', 'debt_payments', 'banktransfer',
                 'credit_card_payments', 'cashledger', 'bank_transaction_ledger', 'credit_card_ledger',
                 'dashboard', 'options', 'stats/yearly?model=expenses', 'stats/yearly/all',
                 'stats/incomings-and-outgoings', 'stats/incomings-and-outgoings/monthly', 'stats/cash-flow',
                 'stats/sources/bank-accounts', 'stats/sources/credit-cards', 'stats/sources/cash',
                 f"bank_accounts/{data['account'].id}/records", f"bank_accounts/{data['account'].id}/reports/yearly",
                 f"bank_accounts/{data['account'].id}/reports/cash-flow", f"bank_accounts/{data['account'].id}/reports/monthly",
                 f"credit_cards/{data['card'].id}/records", f"credit_cards/{data['card'].id}/reports/yearly",
                 f"expense_categories/{data['food'].id}/records", 'expense_categories/reports/monthly'):
        r = client.get('/' + path)
        assert r.status_code == 200, (path, r.get_json())


def test_unauthenticated(app):
    r = app.test_client().get('/expenses', headers={'Accept': 'application/json'})
    assert r.status_code == 401 and r.get_json()['error']['code'] == 'not_authenticated'
    assert app.test_client().post('/expenses', json={}).status_code == 401
    assert 'Log in' in app.test_client().get('/expenses/index').get_data(as_text=True)  # a person gets the login page
    assert app.test_client().get('/session').get_json()['data']['authenticated'] is False


def test_loan_payment_transfer_and_card_payment_flows(client, db, data):
    loan = client.post('/loans', json={'person_name': 'Ana', 'amount': '100', 'is_cash': False,
                                              'bank_account_id': data['account'].id}).get_json()['data']
    assert loan['remaining_amount'] == '100.00'

    pay = client.post('/loan_payments', json={'loan_id': loan['id'], 'amount': '40', 'is_cash': False,
                                                     'bank_account_id': data['account'].id})
    assert pay.status_code == 201, pay.get_json()
    assert client.get(f"/loans/{loan['id']}").get_json()['data']['remaining_amount'] == '60.00'
    assert client.get(f"/loans/{loan['id']}/payments").get_json()['meta']['count'] == 1

    transfer = client.post('/banktransfer', json={
        'from_bank_account_id': data['account'].id, 'to_bank_account_id': data['account2'].id, 'amount': '50'})
    assert transfer.status_code == 201, transfer.get_json()

    card = client.post('/expenses', json={'amount': '30', 'is_cash': False, 'description': 'c',
                                                 'expense_category_id': data['food'].id, 'credit_card_id': data['card'].id})
    assert card.status_code == 201
    payment = client.post('/credit_card_payments', json={
        'credit_card_id': data['card'].id, 'bank_account_id': data['account'].id, 'amount': '30', 'is_cashback': False})
    assert payment.status_code == 201, payment.get_json()
    assert client.delete(f"/credit_card_payments/{payment.get_json()['data']['id']}").status_code == 204
