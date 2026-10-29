"""Safety net for the read-mostly parts: the three ledgers, the stats endpoints, the home page and login."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.models.cash_ledger import CashLedger

from tests.helpers import post_expense


# Ledger rows are dated when they are written (not with the date of the record they belong to),
# so the date filters of the ledgers are tried with a range around today and a range long ago.
TODAY_RANGE = {'start': (date.today() - timedelta(days=1)).isoformat(), 'end': (date.today() + timedelta(days=1)).isoformat()}
LONG_AGO = {'start': '2020-01-01', 'end': '2020-01-31'}


def seed_money_movements(client, data):
    """An expense on a card, an expense paid in cash, an income and a withdrawal, all in October 2026."""
    post_expense(client, amount='10', category=data['food'], card=data['card'], created_at='2026-10-15T12:00')
    post_expense(client, amount='25', category=data['fuel'], cash=True, created_at='2026-10-16T12:00')
    client.post('/incomes', json={
        'amount': '40', 'is_cash': False, 'bank_account_id': data['account'].id, 'created_at': '2026-10-17T12:00'})
    client.post('/withdrawals', json={
        'amount': '60', 'bank_account_id': data['account'].id, 'created_at': '2026-09-02T12:00'})


# ================================================================ cash ledger

def test_cash_ledger_index_renders(client, data):
    seed_money_movements(client, data)

    assert client.get('/cashledger/index').status_code == 200


def test_cash_adjustment_create_and_delete(client):
    created = client.post('/cashledger', json={'amount': '-15.5'})

    assert created.status_code == 201
    adjustment = CashLedger.query.one()
    assert adjustment.type == 'ADJUSTMENT' and adjustment.amount == Decimal('-15.50')
    assert adjustment.reference_code.startswith('ADJ')

    deleted = client.delete(f'/cashledger/{adjustment.id}')

    assert deleted.status_code == 204
    assert CashLedger.query.count() == 0


def test_cash_adjustment_keeps_the_date_it_was_given(client):
    client.post('/cashledger', json={'amount': '5', 'created_at': '2026-09-03T08:15'})

    created = CashLedger.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_cash_adjustment_rejects_bad_amounts(client):
    for amount in ('0', 'abc', ''):
        assert client.post('/cashledger', json={'amount': amount}).status_code in (400, 422), amount

    assert CashLedger.query.count() == 0


def test_only_adjustments_can_be_deleted(client, data):
    post_expense(client, amount='25', category=data['fuel'], cash=True)
    ledger = CashLedger.query.one()

    response = client.delete(f'/cashledger/{ledger.id}')

    assert response.status_code == 400
    assert CashLedger.query.count() == 1


def test_deleting_a_missing_adjustment_is_404(client):
    assert client.delete('/cashledger/999').status_code == 404


def test_cash_ledger_cannot_be_edited_by_hand(client):
    assert client.put('/cashledger/1', json={'amount': '5'}).status_code == 405


def test_cash_ledger_lists_filters_and_reports_the_balance(client, data):
    seed_money_movements(client, data)
    client.post('/cashledger', json={'amount': '5'})

    def types(**params):
        return sorted(row['type'] for row in client.get('/cashledger', query_string=params).get_json()['data'])

    assert types(q='adjust') == ['ADJUSTMENT']
    assert types(q='expense') == ['EXPENSE']

    now = client.get('/cashledger', query_string=TODAY_RANGE).get_json()
    assert sorted(row['type'] for row in now['data']) == ['ADJUSTMENT', 'EXPENSE', 'WITHDRAWAL']
    assert now['meta']['balance'] == '40.00'  # +60 withdrawn, -25 expense, +5 adjustment
    assert client.get('/cashledger', query_string=LONG_AGO).get_json()['data'] == []
    assert client.get('/cashledger', query_string={'start': TODAY_RANGE['start']}).status_code == 422

    both = client.get('/cashledger', query_string={'q': 'adjust', **TODAY_RANGE}).get_json()
    assert [row['type'] for row in both['data']] == ['ADJUSTMENT']
    assert client.get('/cashledger', query_string={'q': 'adjust', **LONG_AGO}).get_json()['data'] == []


# ================================================================ bank account ledger

def test_bank_ledger_index_renders(client, data):
    seed_money_movements(client, data)

    assert client.get('/bank_transaction_ledger/index').status_code == 200


def test_bank_ledger_is_read_only(client):
    assert client.post('/bank_transaction_ledger', json={}).status_code == 405
    assert client.delete('/bank_transaction_ledger/1').status_code == 405


def test_bank_ledger_filters(client, data):
    seed_money_movements(client, data)

    def kinds(**params):
        response = client.get('/bank_transaction_ledger', query_string=params)
        assert response.status_code == 200
        return sorted(row['transaction_type'] for row in response.get_json()['data'])

    assert kinds(q='income') == ['INCOME']
    assert kinds(q='checking') == ['INCOME', 'WITHDRAWAL']
    assert kinds(q='withdrawal') == ['WITHDRAWAL']
    assert kinds(q='checking, income') == ['INCOME']          # "account, type" narrows both
    assert kinds(q='savings, income') == []

    assert kinds(**TODAY_RANGE) == ['INCOME', 'WITHDRAWAL']
    assert kinds(**LONG_AGO) == []
    assert kinds(q='checking', **TODAY_RANGE) == ['INCOME', 'WITHDRAWAL']
    assert kinds(q='checking', **LONG_AGO) == []
    assert client.get('/bank_transaction_ledger', query_string={'end': '2026-10-31'}).status_code == 422


# ================================================================ credit card ledger

def test_credit_card_ledger_index_renders(client, data):
    seed_money_movements(client, data)

    assert client.get('/credit_card_ledger/ledger').status_code == 200


def test_credit_card_ledger_filters(client, data):
    seed_money_movements(client, data)

    def kinds(**params):
        body = client.get('/credit_card_ledger', query_string=params).get_json()
        return [row['transaction_type'] for row in body['data']]

    assert kinds(q='visa') == ['EXPENSE']
    assert kinds(q='master') == []
    assert kinds(q='visa, expense') == ['EXPENSE']
    assert kinds(q='visa, loan') == []

    assert len(kinds(**TODAY_RANGE)) == 1
    assert kinds(**LONG_AGO) == []
    assert client.get('/credit_card_ledger', query_string={'start': '2026-10-01'}).status_code == 422


# ================================================================ stats

def test_stats_yearly_single_model_report(client, data):
    seed_money_movements(client, data)

    body = client.get('/stats/yearly', query_string={'model': 'expenses', 'year': 2026}).get_json()['data']

    assert len(body['months']) == 12 and body['label'] == 'Expenses'
    assert float(body['expenses'][9]) == 35.0
    assert client.get('/stats/yearly', query_string={'model': 'nope', 'year': 2026}).status_code == 400


def test_stats_yearly_all_model_reports(client, data):
    seed_money_movements(client, data)

    report = client.get('/stats/yearly/all', query_string={'year': 2026}).get_json()['data']['report']

    assert float(report['expenses'][9]) == 35.0 and float(report['incomes'][9]) == 40.0
    assert float(report['withdrawals'][8]) == 60.0
    assert 'bank_transfers' in report


def test_stats_incomes_and_outgoings(client, data):
    seed_money_movements(client, data)

    body = client.get('/stats/incomings-and-outgoings', query_string={'year': 2026}).get_json()['data']

    assert float(body['incomings'][9]) == 40.0
    assert float(body['outgoings'][9]) == 35.0 and float(body['outgoings'][8]) == 60.0


def test_stats_monthly_incomings_and_outgoings(client, data):
    this_month = datetime.now().strftime('%Y-%m-%dT%H:%M')
    post_expense(client, amount='12', category=data['food'], cash=True, created_at=this_month)
    client.post('/incomes', json={'amount': '30', 'is_cash': True, 'created_at': this_month})

    body = client.get('/stats/incomings-and-outgoings/monthly').get_json()['data']

    assert float(body['incomings']) == 30.0 and float(body['outgoings']) == 12.0


def test_stats_reports_by_source(client, data):
    seed_money_movements(client, data)

    bank = client.get('/stats/sources/bank-accounts', query_string={'year': 2026}).get_json()['data']['report']
    assert float(bank['incomes'][9]) == 40.0 and float(bank['withdrawals'][8]) == 60.0
    assert 'bank_transfers' in bank and 'expenses' in bank

    card = client.get('/stats/sources/credit-cards', query_string={'year': 2026}).get_json()['data']['report']
    assert float(card['expenses'][9]) == 10.0

    cash = client.get('/stats/sources/cash', query_string={'year': 2026}).get_json()['data']['report']
    assert float(cash['expenses'][9]) == 25.0


def test_stats_cash_flow(client, data):
    seed_money_movements(client, data)

    report = client.get('/stats/cash-flow', query_string={'year': 2026}).get_json()['data']['report']

    assert float(report['expenses'][9]) == 35.0 and float(report['incomes'][9]) == 40.0
    assert float(report['balances'][9]) == 5.0


def test_stats_reject_a_bad_year(client):
    assert client.get('/stats/cash-flow', query_string={'year': 'abc'}).status_code == 400
    assert client.get('/stats/cash-flow', query_string={'year': 1900}).status_code == 400


# ================================================================ home and login

def test_home_page_and_dashboard(client, data):
    this_month = datetime.now().strftime('%Y-%m-%dT%H:%M')
    post_expense(client, amount='12', category=data['food'], cash=True, created_at=this_month)
    client.post('/incomes', json={'amount': '30', 'is_cash': True, 'created_at': this_month})

    assert client.get('/').status_code == 200

    dashboard = client.get('/dashboard').get_json()['data']
    assert float(dashboard['month']['incomes']) == 30.0 and float(dashboard['month']['expenses']) == 12.0
    assert dashboard['cash_balance'] == '18.00'


def test_options_for_the_forms(client, data):
    options = client.get('/options').get_json()['data']

    assert [b['name'] for b in options['banks']] == ['Test Bank']
    assert {a['nick_name'] for a in options['bank_accounts']} == {'Checking', 'Savings'}
    assert {c['nick_name'] for c in options['credit_cards']} == {'Visa', 'Master'}
    assert len(options['expense_categories']) == 2 and options['years']


def test_everything_asks_for_a_login(app):
    anonymous = app.test_client()
    asks_json = {'Accept': 'application/json'}

    for path in ('/expenses', '/stats/cash-flow', '/dashboard', '/options', '/bank_accounts/1/records'):
        response = anonymous.get(path, headers=asks_json)
        assert response.status_code == 401, path
        assert response.get_json()['error']['code'] == 'not_authenticated'

    for path in ('/', '/expenses/index', '/incomes/index', '/banks/index'):
        assert b'Log in' in anonymous.get(path).data, path

    assert anonymous.post('/expenses', json={}).status_code == 401
    assert anonymous.delete('/expenses/1').status_code == 401


def test_login_page_renders(app):
    assert app.test_client().get('/login').status_code == 200


def login(client, username, password):
    return client.post('/login', json={'username': username, 'password': password})


def test_login_with_a_wrong_password_is_a_401_with_a_message(app, db):
    import bcrypt
    from app.models.user import User

    db.session.add(User(username='alice', password=bcrypt.hashpw(b'secret', bcrypt.gensalt())))
    db.session.commit()

    response = login(app.test_client(), 'alice', 'nope')

    assert response.status_code == 401
    assert response.get_json()['error']['message'] == 'Wrong username or password.'


def test_login_with_a_malformed_stored_password_just_fails(app, data):
    response = login(app.test_client(), 'tester', 'whatever')

    assert response.status_code == 401
    assert response.get_json()['error']['code'] == 'wrong_credentials'


def test_login_without_credentials_is_a_validation_error(app):
    assert app.test_client().post('/login', json={}).status_code == 422


def test_login_session_and_logout(app, db):
    import bcrypt
    from app.models.user import User

    db.session.add(User(username='alice', password=bcrypt.hashpw(b'secret', bcrypt.gensalt())))
    db.session.commit()
    client = app.test_client()

    assert client.get('/session').get_json()['data']['authenticated'] is False

    response = login(client, 'alice', 'secret')
    assert response.status_code == 200 and response.get_json()['data']['username'] == 'alice'
    session = client.get('/session').get_json()['data']
    assert session['authenticated'] is True and session['user']['username'] == 'alice' and session['csrf_token']
    assert client.get('/expenses').status_code == 200

    assert client.post('/logout').status_code == 204
    assert client.get('/expenses', headers={'Accept': 'application/json'}).status_code == 401
