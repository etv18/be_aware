"""Every page is a real HTML template with its own script: check it renders, loads its script and that nothing imports a missing file."""
import os

import pytest

# every page is a real HTML template with its own script: (url, the script the page loads)
PAGES = [
    ('/', 'home'), ('/banks', 'banks'), ('/bank_accounts', 'bank_accounts'),
    ('/bank_accounts/1', 'bank_account'), ('/credit_cards', 'credit_cards'),
    ('/credit_cards/1', 'credit_card'), ('/expense_categories', 'expense_categories'),
    ('/expense_categories/1', 'expense_category'), ('/expenses', 'expenses'),
    ('/incomes', 'incomes'), ('/withdrawals', 'withdrawals'), ('/deposits', 'deposits'),
    ('/loans', 'loans'), ('/loans/1', 'loan'),
    ('/loan_payments', 'loan_payments'), ('/debts', 'debts'),
    ('/debts/1', 'debt'), ('/debt_payments', 'debt_payments'),
    ('/cash_ledger', 'cash_ledger'), ('/bank_ledger', 'bank_ledger'),
    ('/card_ledger', 'card_ledger'),
]


@pytest.mark.parametrize('url,script', PAGES)
def test_page_is_real_html_with_its_own_script(client, app, url, script):
    response = client.get(url)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'js/{script}.js' in html
    assert 'name="csrf-token"' in html
    assert 'id="app"' not in html  # no empty shell any more: the markup is in the template
    assert os.path.exists(os.path.join(app.static_folder, 'js', f'{script}.js'))


def test_every_script_the_pages_import_exists(app):
    """Each page script imports ./common.js, ./chart.js, ./forms.js or ./records.js: they must all be there."""
    import re

    js = os.path.join(app.static_folder, 'js')
    for name in os.listdir(js):
        if not name.endswith('.js'):
            continue
        source = open(os.path.join(js, name), encoding='utf-8').read()
        for target in re.findall(r"from '\./([\w./-]+)'", source):
            assert os.path.exists(os.path.join(js, target)), f'{name} imports ./{target}'


def test_expenses_page_has_its_list_form_and_confirmation(client):
    html = client.get('/expenses').get_data(as_text=True)
    for piece in ('data-rows', 'data-row-template', 'id="record-dialog"', 'id="confirm-dialog"', 'data-filters', 'data-chart'):
        assert piece in html, piece


def test_detail_page_carries_the_record_id(client):
    assert 'data-id="7"' in client.get('/loans/7').get_data(as_text=True)


def test_api_rejects_unsafe_requests_without_a_csrf_token(app, data):
    app.config['WTF_CSRF_ENABLED'] = True
    client = app.test_client()
    with client.session_transaction() as s:
        s['_user_id'] = str(data['user'].id)

    body = {'amount': '10', 'is_cash': True, 'expense_category_id': data['food'].id, 'description': 'x'}
    refused = client.post('/api/expenses', json=body)
    assert refused.status_code == 400 and refused.get_json()['error']['code'] == 'csrf_failed'

    token = client.get('/api/session').get_json()['data']['csrf_token']
    accepted = client.post('/api/expenses', json=body, headers={'X-CSRFToken': token})
    assert accepted.status_code == 201, accepted.get_json()


def test_the_navbar_groups_the_modules_and_shows_the_environment(client):
    html = client.get('/expenses').get_data(as_text=True)

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
