"""Pages are an empty shell that the page script fills from the JSON endpoints: check the shell and the script exist."""
import os

import pytest

PAGES = [
    ('/', 'home'), ('/banks/index', 'banks'), ('/bank_accounts/index', 'bank-accounts'),
    ('/bank_accounts/associated_records/1', 'bank-account'), ('/credit_cards/index', 'credit-cards'),
    ('/credit_cards/associated_records/1', 'credit-card'), ('/expense_categories/index', 'expense-categories'),
    ('/expense_categories/associated_records/1', 'expense-category'), ('/expenses/index', 'expenses'),
    ('/incomes/index', 'incomes'), ('/withdrawals/index', 'withdrawals'), ('/deposits/index', 'deposits'),
    ('/loans/index', 'loans'), ('/loans/associated_records/1', 'loan'),
    ('/loan_payments/index', 'loan-payments'), ('/debts/index', 'debts'),
    ('/debts/associated/records/1', 'debt'), ('/debt_payments/index', 'debt-payments'),
    ('/cashledger/index', 'cash-ledger'), ('/bank_transaction_ledger/index', 'bank-ledger'),
    ('/credit_card_ledger/ledger', 'card-ledger'),
]


@pytest.mark.parametrize('url,script', PAGES)
def test_page_is_a_shell_with_its_script(client, app, url, script):
    response = client.get(url)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="app"' in html and f'js/pages/{script}.js' in html
    assert 'name="csrf-token"' in html
    assert os.path.exists(os.path.join(app.static_folder, 'js', 'pages', f'{script}.js'))


def test_detail_page_carries_the_record_id(client):
    assert 'data-id="7"' in client.get('/loans/associated_records/7').get_data(as_text=True)


def test_api_rejects_unsafe_requests_without_a_csrf_token(app, data):
    app.config['WTF_CSRF_ENABLED'] = True
    client = app.test_client()
    with client.session_transaction() as s:
        s['_user_id'] = str(data['user'].id)

    body = {'amount': '10', 'is_cash': True, 'expense_category_id': data['food'].id, 'description': 'x'}
    refused = client.post('/expenses', json=body)
    assert refused.status_code == 400 and refused.get_json()['error']['code'] == 'csrf_failed'

    token = client.get('/session').get_json()['data']['csrf_token']
    accepted = client.post('/expenses', json=body, headers={'X-CSRFToken': token})
    assert accepted.status_code == 201, accepted.get_json()


def test_the_navbar_groups_the_modules_and_shows_the_environment(client):
    html = client.get('/expenses/index').get_data(as_text=True)

    for group in ('Cash flow', 'Bank products', 'Cash', 'Lending'):
        assert group in html
    assert html.count('data-menu-trigger') == 4
    assert 'data-env="testing"' in html and '>TEST<' in html
    assert '[TEST]' in html  # also in the tab title, so a dev tab is never mistaken for the real one


def test_each_environment_has_its_own_badge():
    from app.config import get_config

    assert get_config('development').ENV_LABEL == 'DEV'
    assert get_config('testing').ENV_LABEL == 'TEST'
    assert get_config('production').ENV_LABEL == 'PROD'
