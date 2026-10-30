"""Read side of the expenses module: the JSON endpoints the filters on the page call."""
from tests.helpers import post_expense


def make_expenses(client, data):
    post_expense(client, amount='100', category=data['food'], description='Pizza night', cash=True, created_at='2026-10-15T12:30')
    post_expense(client, amount='50.25', category=data['fuel'], description='Gas station', account=data['account'], created_at='2026-10-20T08:00')
    post_expense(client, amount='10', category=data['food'], description='Old coffee', card=data['card'], created_at='2026-09-01T09:00')


def test_index_page_renders(client, data):
    make_expenses(client, data)

    response = client.get('/expenses')

    assert response.status_code == 200
    assert b'Expenses' in response.data


def test_index_requires_login(app):
    response = app.test_client().get('/expenses')

    assert b'login' in response.data.lower()


def test_filter_by_time_returns_only_the_expenses_in_range(client, data):
    make_expenses(client, data)

    response = client.get('/api/expenses', query_string={'start': '2026-10-01', 'end': '2026-10-31'})

    body = response.get_json()
    assert response.status_code == 200
    assert sorted(e['description'] for e in body['data']) == ['Gas station', 'Pizza night']
    assert body['meta']['total'] == '150.25'


def test_filter_by_time_with_only_one_date_is_a_client_error(client):
    response = client.get('/api/expenses', query_string={'start': '2026-10-01'})

    assert response.status_code == 422
    assert response.get_json()['error']['code'] == 'validation_error'


def test_filter_by_a_bad_date_is_a_client_error(client):
    response = client.get('/api/expenses', query_string={'start': 'soon', 'end': '2026-10-31'})

    assert response.status_code == 400
    assert response.get_json()['error']['code'] == 'invalid_value'


def test_filter_by_is_cash(client, data):
    make_expenses(client, data)

    cash = client.get('/api/expenses', query_string={'q': 'yes'}).get_json()
    not_cash = client.get('/api/expenses', query_string={'q': 'no'}).get_json()

    assert cash['meta']['count'] == 1 and cash['data'][0]['description'] == 'Pizza night'
    assert not_cash['meta']['count'] == 2


def test_filter_by_field_matches_description_account_and_category(client, data):
    make_expenses(client, data)

    for query, expected in (('pizza', 1), ('Checking', 1), ('FUEL', 1), ('Visa', 1), ('nothing-matches', 0)):
        body = client.get('/api/expenses', query_string={'q': query}).get_json()
        assert body['meta']['count'] == expected, query


def test_filter_combines_text_and_dates(client, data):
    make_expenses(client, data)

    body = client.get('/api/expenses', query_string={'q': 'o', 'start': '2026-10-01', 'end': '2026-10-31'}).get_json()

    assert sorted(e['description'] for e in body['data']) == ['Gas station', 'Pizza night']


def test_the_list_reports_the_budget_of_the_month(client, data):
    make_expenses(client, data)

    meta = client.get('/api/expenses').get_json()['meta']

    assert 'budget' in meta


def test_an_expense_can_be_read_one_by_one(client, data):
    make_expenses(client, data)
    expense_id = client.get('/api/expenses').get_json()['data'][0]['id']

    assert client.get(f'/api/expenses/{expense_id}').status_code == 200
    assert client.get('/api/expenses/999').status_code == 404
