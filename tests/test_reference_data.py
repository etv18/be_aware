"""Safety net for the records the money flows hang from: banks, bank accounts, credit cards and
expense categories."""
from datetime import datetime
from decimal import Decimal

from app.models.bank import Bank
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.models.expense_category import ExpenseCategory

from tests.helpers import post_expense


def body_of(response):
    return response.get_json()['data']


# ================================================================ banks

def test_bank_create_update_delete(client):
    created = client.post('/api/banks', json={'name': 'Big Bank'})
    assert created.status_code == 201
    bank = Bank.query.filter_by(name='Big Bank').one()

    updated = client.put(f'/api/banks/{bank.id}', json={'name': 'Bigger Bank'})
    assert updated.status_code == 200
    assert Bank.query.filter_by(name='Bigger Bank').count() == 1

    deleted = client.delete(f'/api/banks/{bank.id}')
    assert deleted.status_code == 204
    assert Bank.query.filter_by(name='Bigger Bank').count() == 0


def test_bank_update_of_a_missing_bank_is_404(client):
    response = client.put('/api/banks/999', json={'name': 'Ghost'})

    assert response.status_code == 404
    assert Bank.query.filter_by(name='Ghost').count() == 0


def test_bank_needs_a_name(client):
    assert client.post('/api/banks', json={'name': ''}).status_code == 422
    assert client.post('/api/banks', json={}).status_code == 422


def test_bank_with_accounts_cannot_be_deleted(client, data):
    response = client.delete(f"/api/banks/{data['bank'].id}")

    assert response.status_code == 400
    assert Bank.query.get(data['bank'].id) is not None


def test_bank_delete_of_a_missing_bank_is_404(client):
    assert client.delete('/api/banks/999').status_code == 404


def test_bank_index_renders(client):
    assert client.get('/banks').status_code == 200


# ================================================================ bank accounts

def account_form(nick='Main', amount='250', number='123456', bank=None):
    return {'nick_name': nick, 'amount_available': amount, 'account_number': number, 'bank_id': bank.id}


def test_bank_account_create(client, data):
    response = client.post('/api/bank_accounts', json=account_form(bank=data['bank']))

    assert response.status_code == 201
    account = BankAccount.query.filter_by(nick_name='Main').one()
    assert account.amount_available == Decimal('250.00')
    assert account.account_number == '123456' and account.bank_id == data['bank'].id
    assert account.is_deleted is False


def test_bank_account_create_rejects_bad_amounts(client, data):
    for amount in ('0', '-5', 'abc'):
        response = client.post('/api/bank_accounts', json=account_form(amount=amount, bank=data['bank']))
        assert response.status_code in (400, 422), amount

    assert BankAccount.query.filter_by(nick_name='Main').count() == 0


def test_bank_account_update(client, data):
    form = account_form(nick='Renamed', number='654321', amount='777.50', bank=data['bank'])

    response = client.put(f"/api/bank_accounts/{data['account'].id}", json=form)

    assert response.status_code == 200
    account = BankAccount.query.get(data['account'].id)
    assert (account.nick_name, account.account_number, account.amount_available) == ('Renamed', '654321', Decimal('777.50'))


def test_bank_account_update_rejects_a_bad_amount_and_changes_nothing(client, db, data):
    form = account_form(nick='Renamed', number='1', amount='-1', bank=data['bank'])

    response = client.put(f"/api/bank_accounts/{data['account'].id}", json=form)

    assert response.status_code in (400, 422)
    db.session.expire_all()
    assert BankAccount.query.get(data['account'].id).nick_name == 'Checking'


def test_bank_account_update_of_a_missing_account_is_404(client, data):
    assert client.put('/api/bank_accounts/999', json=account_form(nick='x', number='1', amount='5', bank=data['bank'])).status_code == 404


def test_bank_account_delete_hides_it(client, db, data):
    response = client.delete(f"/api/bank_accounts/{data['account2'].id}")

    assert response.status_code == 204
    db.session.expire_all()
    assert BankAccount.query.get(data['account2'].id).is_deleted is True
    assert 'Savings' not in [a['nick_name'] for a in client.get('/api/bank_accounts').get_json()['data']]


def test_bank_account_delete_of_a_missing_account_is_404(client):
    assert client.delete('/api/bank_accounts/999').status_code == 404


def test_bank_account_pages_render(client, data):
    post_expense(client, amount='10', category=data['food'], account=data['account'])
    account_id = data['account'].id

    assert client.get('/bank_accounts').status_code == 200
    assert client.get(f'/bank_accounts/{account_id}').status_code == 200


def test_bank_account_records(client, data):
    post_expense(client, amount='10', category=data['food'], account=data['account'])

    body = body_of(client.get(f"/api/bank_accounts/{data['account'].id}/records"))

    assert body['bank_account']['id'] == data['account'].id
    assert len(body['records']['expenses']) == 1
    assert client.get('/api/bank_accounts/999/records').status_code == 404


def test_bank_account_reports(client, data):
    account_id = data['account'].id
    post_expense(client, amount='10', category=data['food'], account=data['account'], created_at='2026-10-15T12:00')
    client.post('/api/incomes', json={'amount': '40', 'is_cash': False, 'bank_account_id': account_id, 'created_at': '2026-10-16T12:00'})
    client.post('/api/bank_transfers', json={
        'amount': '100', 'from_bank_account_id': account_id, 'to_bank_account_id': data['account2'].id,
        'created_at': '2026-10-17T12:00',
    })

    flow = body_of(client.get(f'/api/bank_accounts/{account_id}/reports/cash_flow', query_string={'year': 2026}))
    assert len(flow['months']) == 12
    assert float(flow['outgoings'][9]) == 110.0   # the expense and the outgoing transfer
    assert float(flow['incomings'][9]) == 40.0
    assert float(flow['balances'][9]) == -70.0

    per_association = body_of(client.get(f'/api/bank_accounts/{account_id}/reports/yearly', query_string={'year': 2026}))
    info = per_association['associations_info']
    assert float(info['expenses'][9]) == 10.0 and float(info['incomes'][9]) == 40.0
    assert float(info['outgoing_transfers'][9]) == 100.0

    monthly = client.get(f'/api/bank_accounts/{account_id}/reports/monthly')
    assert monthly.status_code == 200
    assert 'transfers_outgoings' in body_of(monthly)['monthly_totals']

    assert client.get('/api/bank_accounts/999/reports/yearly').status_code == 404
    assert client.get(f'/api/bank_accounts/{account_id}/reports/yearly', query_string={'year': 'abc'}).status_code == 400


# ================================================================ credit cards

def card_form(nick='Gold', amount='400', limit='500', bank=None):
    return {'nick_name': nick, 'amount_available': amount, 'limit': limit, 'bank_id': bank.id}


def test_credit_card_create(client, data):
    response = client.post('/api/credit_cards', json=card_form(bank=data['bank']))

    assert response.status_code == 201
    card = CreditCard.query.filter_by(nick_name='Gold').one()
    assert (card.limit, card.amount_available) == (Decimal('500.00'), Decimal('400.00'))


def test_credit_card_create_rejects_bad_amounts(client, data):
    for amount, limit in (('0', '500'), ('-5', '500'), ('abc', '500'), ('10', 'abc')):
        response = client.post('/api/credit_cards', json=card_form(amount=amount, limit=limit, bank=data['bank']))
        assert response.status_code in (400, 422), (amount, limit)

    assert CreditCard.query.filter_by(nick_name='Gold').count() == 0


def test_credit_card_update(client, data):
    form = card_form(nick='Platinum', amount='650', limit='900', bank=data['bank'])

    response = client.put(f"/api/credit_cards/{data['card'].id}", json=form)

    assert response.status_code == 200
    card = CreditCard.query.get(data['card'].id)
    assert (card.nick_name, card.limit, card.amount_available) == ('Platinum', Decimal('900.00'), Decimal('650.00'))


def test_credit_card_update_of_a_missing_card_is_404(client, data):
    assert client.put('/api/credit_cards/999', json=card_form(nick='x', amount='5', limit='9', bank=data['bank'])).status_code == 404


def test_credit_card_delete_hides_it(client, db, data):
    response = client.delete(f"/api/credit_cards/{data['card2'].id}")

    assert response.status_code == 204
    db.session.expire_all()
    assert CreditCard.query.get(data['card2'].id).is_deleted is True
    assert 'Master' not in [c['nick_name'] for c in client.get('/api/credit_cards').get_json()['data']]


def test_credit_card_delete_of_a_missing_card_is_404(client):
    assert client.delete('/api/credit_cards/999').status_code == 404


def test_credit_card_pages_and_records(client, data):
    post_expense(client, amount='10', category=data['food'], card=data['card'], created_at='2026-10-15T12:00')
    card_id = data['card'].id

    assert client.get('/credit_cards').status_code == 200
    assert client.get(f'/credit_cards/{card_id}').status_code == 200

    body = body_of(client.get(f'/api/credit_cards/{card_id}/records'))
    assert len(body['records']['expenses']) == 1
    assert client.get('/api/credit_cards/999/records').status_code == 404

    yearly = body_of(client.get(f'/api/credit_cards/{card_id}/reports/yearly', query_string={'year': 2026}))
    assert float(yearly['associations_info']['expenses'][9]) == 10.0


# ================================================================ expense categories

def test_category_create(client):
    response = client.post('/api/expense_categories', json={'name': 'travel', 'limit': '150'})

    assert response.status_code == 201
    category = ExpenseCategory.query.filter_by(name='TRAVEL').one()
    assert category.limit == Decimal('150.00')


def test_category_create_rejects_bad_input(client):
    for name, limit in (('abc', '10'), ('', '10'), ('travel', '-1'), ('travel', 'abc')):
        response = client.post('/api/expense_categories', json={'name': name, 'limit': limit})
        assert response.status_code in (400, 422), (name, limit)

    assert ExpenseCategory.query.filter_by(name='TRAVEL').count() == 0


def test_category_update(client, data):
    response = client.put(f"/api/expense_categories/{data['food'].id}", json={'name': 'groceries', 'limit': '320'})

    assert response.status_code == 200
    category = ExpenseCategory.query.get(data['food'].id)
    assert category.name == 'GROCERIES' and category.limit == Decimal('320.00')


def test_category_update_of_a_missing_category_is_404(client):
    assert client.put('/api/expense_categories/999', json={'name': 'groceries', 'limit': '3'}).status_code == 404


def test_category_delete_hides_it_but_keeps_its_expenses(client, db, data):
    post_expense(client, amount='10', category=data['fuel'], cash=True)

    response = client.delete(f"/api/expense_categories/{data['fuel'].id}")

    assert response.status_code == 204
    db.session.expire_all()
    assert ExpenseCategory.query.get(data['fuel'].id).is_deleted is True
    assert client.get(f"/api/expense_categories/{data['fuel'].id}/records").status_code == 404


def test_category_delete_of_a_missing_category_is_404(client):
    assert client.delete('/api/expense_categories/999').status_code == 404


def test_category_pages_and_records(client, data):
    post_expense(client, amount='10', category=data['food'], cash=True)
    category_id = data['food'].id

    assert client.get('/expense_categories').status_code == 200
    assert client.get(f'/expense_categories/{category_id}').status_code == 200

    body = body_of(client.get(f'/api/expense_categories/{category_id}/records'))
    assert len(body['records']['expenses']) == 1
    assert client.get('/api/expense_categories/999/records').status_code == 404


def test_category_monthly_report_lines_names_up_with_totals_even_after_a_delete(client, data):
    this_month = datetime.now().strftime('%Y-%m-%dT%H:%M')
    post_expense(client, amount='10', category=data['food'], cash=True, created_at=this_month)
    post_expense(client, amount='7', category=data['fuel'], cash=True, created_at=this_month)
    client.delete(f"/api/expense_categories/{data['food'].id}")

    body = body_of(client.get('/api/expense_categories/reports/monthly'))

    assert body['names'] == ['Fuel']
    assert [float(total) for total in body['totals']] == [7.0]
