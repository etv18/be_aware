"""Safety net for debts (money borrowed) and debt payments (money paid back).

A debt brings money into cash or a bank account. Each payment takes money out of cash or a bank
account, and the debt is "paid" (is_active False) once the payments cover it.
"""
from decimal import Decimal

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment

def debt_form(amount, person='Carlos', description='Car repair', account=None, cash=False,
              created_at='2026-10-15T12:30', paid=False):
    """The JSON body the debt form sends."""
    return {
        'amount': str(amount),
        'person_name': person,
        'description': description,
        'created_at': created_at,
        'bank_account_id': account.id if account else None,
        'is_cash': cash,
        'is_active': not paid,  # the edit dialog's "mark as paid" switch
    }


def payment_form(debt_id, amount, account=None, cash=False, created_at='2026-10-16T09:00'):
    return {
        'debt_id': debt_id,
        'amount': str(amount),
        'created_at': created_at,
        'bank_account_id': account.id if account else None,
        'is_cash': cash,
    }


def create_debt(client, **kwargs):
    return client.post('/api/debts', json=debt_form(**kwargs))


def update_debt(client, debt_id, **kwargs):
    return client.put(f'/api/debts/{debt_id}', json=debt_form(**kwargs))


def delete_debt(client, debt_id):
    return client.delete(f'/api/debts/{debt_id}')


def pay(client, debt_id, **kwargs):
    return client.post('/api/debt_payments', json=payment_form(debt_id, **kwargs))


def update_payment(client, payment_id, debt_id, **kwargs):
    body = payment_form(debt_id, **kwargs)
    del body['debt_id']
    return client.put(f'/api/debt_payments/{payment_id}', json=body)


def delete_payment(client, payment_id):
    return client.delete(f'/api/debt_payments/{payment_id}')


def balance(db, account):
    db.session.expire_all()
    return account.amount_available


def only_debt():
    return Debt.query.one()


def cash_of(kind):
    return CashLedger.query.filter(CashLedger.type == kind)


def boom(*args, **kwargs):
    raise RuntimeError('ledger is down')


# ================================================================ debts: create

def test_debt_into_a_bank_account(client, db, data):
    response = create_debt(client, amount='300', account=data['account'])

    assert response.status_code == 201
    debt = only_debt()
    assert debt.code.startswith('DEBT')
    assert debt.is_active is True and debt.is_cash is False
    assert balance(db, data['account']) == Decimal('1300.00')

    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('300.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('1300.00')
    assert CashLedger.query.count() == 0


def test_cash_debt(client, db, data):
    response = create_debt(client, amount='80', cash=True)

    assert response.status_code == 201
    assert CashLedger.query.one().amount == Decimal('80.00')
    assert only_debt().is_cash is True
    assert balance(db, data['account']) == Decimal('1000.00')


def test_debt_without_a_bank_product_is_still_allowed(client, db, data):
    response = create_debt(client, amount='20')  # not cash and no account selected

    assert response.status_code == 201
    assert only_debt().bank_account_id is None
    assert CashLedger.query.count() == 0 and BankAccountTransactionsLedger.query.count() == 0


def test_debt_keeps_the_date_it_was_given(client):
    create_debt(client, amount='10', cash=True, created_at='2026-09-03 08:15')

    created = only_debt().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_debt_without_a_date_uses_now(client):
    response = client.post('/api/debts', json={'amount': '10', 'person_name': 'C', 'is_cash': True})

    assert response.status_code == 201
    assert only_debt().created_at is not None


def test_debt_rejects_bad_amounts(client):
    for amount in ('0', '-5', 'abc'):
        assert create_debt(client, amount=amount, cash=True).status_code in (400, 422), amount

    assert Debt.query.count() == 0


def test_debt_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(boom))

    response = create_debt(client, amount='300', account=data['account'])

    assert response.status_code == 500
    assert Debt.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


# ================================================================ debts: update

def test_debt_update_amount_on_the_same_account(client, db, data):
    create_debt(client, amount='300', account=data['account'])

    response = update_debt(client, only_debt().id, amount='500', account=data['account'], person='Carlos B')

    assert response.status_code == 200
    debt = only_debt()
    assert debt.amount == Decimal('500.00') and debt.person_name == 'Carlos B'
    assert balance(db, data['account']) == Decimal('1500.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('500.00')


def test_debt_update_to_another_account(client, db, data):
    create_debt(client, amount='300', account=data['account'])

    update_debt(client, only_debt().id, amount='300', account=data['account2'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('800.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_debt_update_to_cash_and_back(client, db, data):
    create_debt(client, amount='300', account=data['account'])
    debt_id = only_debt().id

    update_debt(client, debt_id, amount='300', cash=True)

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.one().amount == Decimal('300.00')

    update_debt(client, debt_id, amount='300', account=data['account'])

    assert balance(db, data['account']) == Decimal('1300.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 1


def test_debt_update_to_no_bank_product_takes_the_money_back_out(client, db, data):
    create_debt(client, amount='300', account=data['account'])

    update_debt(client, only_debt().id, amount='300')  # not cash, nothing selected

    assert balance(db, data['account']) == Decimal('1000.00')
    assert only_debt().bank_account_id is None
    assert BankAccountTransactionsLedger.query.count() == 0


def test_debt_update_can_mark_it_as_paid(client):
    create_debt(client, amount='50', cash=True)

    update_debt(client, only_debt().id, amount='50', cash=True, paid=True)
    assert only_debt().is_active is False

    update_debt(client, only_debt().id, amount='50', cash=True)
    assert only_debt().is_active is True


def test_debt_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_debt(client, amount='300', account=data['account'])
    monkeypatch.setattr(BankAccountTransactionsLedger, 'update', staticmethod(boom))

    response = update_debt(client, only_debt().id, amount='400', account=data['account'])

    assert response.status_code == 500
    assert only_debt().amount == Decimal('300.00')
    assert balance(db, data['account']) == Decimal('1300.00')


def test_debt_update_of_a_missing_debt_is_404(client):
    assert update_debt(client, 999, amount='10', cash=True).status_code == 404


# ================================================================ debts: delete

def test_debt_delete_takes_the_money_back_and_removes_ledgers(client, db, data):
    create_debt(client, amount='300', account=data['account'])
    create_debt(client, amount='50', cash=True)

    for debt in Debt.query.all():
        assert delete_debt(client, debt.id).status_code == 204

    assert Debt.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.count() == 0


def test_debt_delete_also_undoes_its_payments(client, db, data):
    create_debt(client, amount='300', account=data['account'])
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account2'])
    pay(client, debt_id, amount='50', cash=True)

    response = delete_debt(client, debt_id)

    assert response.status_code == 204
    assert Debt.query.count() == 0 and DebtPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('500.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.count() == 0


def test_debt_without_a_bank_product_can_be_deleted(client):
    create_debt(client, amount='20')

    assert delete_debt(client, only_debt().id).status_code == 204
    assert Debt.query.count() == 0


def test_debt_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_debt(client, amount='300', account=data['account'])
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(boom))

    response = delete_debt(client, only_debt().id)

    assert response.status_code == 500
    assert Debt.query.count() == 1
    assert balance(db, data['account']) == Decimal('1300.00')


def test_debt_delete_of_a_missing_debt_is_404(client):
    assert delete_debt(client, 999).status_code == 404


# ================================================================ debt payments

def test_payment_from_a_bank_account(client, db, data):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id

    response = pay(client, debt_id, amount='100', account=data['account'])

    assert response.status_code == 201
    payment = DebtPayment.query.one()
    assert payment.code.startswith('DPMT') and payment.debt_id == debt_id
    assert balance(db, data['account']) == Decimal('900.00')
    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('-100.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('900.00')
    assert only_debt().is_active is True
    assert only_debt().remaining_amount() == Decimal('200.00')


def test_cash_payment(client):
    create_debt(client, amount='300', cash=True)

    response = pay(client, only_debt().id, amount='100', cash=True)

    assert response.status_code == 201
    assert cash_of('DEBT PAYMENT').one().amount == Decimal('-100.00')
    assert DebtPayment.query.one().bank_account_id is None


def test_payment_with_more_than_the_available_money_changes_nothing(client, db, data):
    create_debt(client, amount='300', cash=True)

    response = pay(client, only_debt().id, amount='5000', account=data['account'])

    assert response.status_code == 400
    assert 'Insufficient' in response.get_json()['error']['message']
    assert DebtPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_debt_is_marked_as_paid_when_the_payments_cover_it(client):
    create_debt(client, amount='100', cash=True)
    debt_id = only_debt().id

    pay(client, debt_id, amount='40', cash=True)
    assert only_debt().is_active is True

    pay(client, debt_id, amount='60', cash=True)
    assert only_debt().is_active is False


def test_a_fully_paid_debt_takes_no_more_payments(client):
    create_debt(client, amount='100', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', cash=True)

    response = pay(client, debt_id, amount='10', cash=True)

    assert response.status_code == 400
    assert response.get_json()['error']['code'] == 'debt_already_paid'
    assert DebtPayment.query.count() == 1


def test_payment_for_a_missing_debt_is_404(client):
    assert pay(client, 999, amount='10', cash=True).status_code == 404


def test_payment_rejects_bad_amounts_and_a_missing_account(client):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id

    for amount in ('0', '-5', 'abc'):
        assert pay(client, debt_id, amount=amount, cash=True).status_code in (400, 422), amount
    assert pay(client, debt_id, amount='10').status_code == 400  # not cash and no account

    assert DebtPayment.query.count() == 0


def test_payment_keeps_the_date_it_was_given(client):
    create_debt(client, amount='300', cash=True)

    pay(client, only_debt().id, amount='10', cash=True, created_at='2026-09-03 08:15')

    created = DebtPayment.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_payment_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_debt(client, amount='300', cash=True)
    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(boom))

    response = pay(client, only_debt().id, amount='100', account=data['account'])

    assert response.status_code == 500
    assert DebtPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_payment_update_amount_on_the_same_account(client, db, data):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'])

    response = update_payment(client, DebtPayment.query.one().id, debt_id, amount='250', account=data['account'])

    assert response.status_code == 200
    assert DebtPayment.query.one().amount == Decimal('250.00')
    assert balance(db, data['account']) == Decimal('750.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('-250.00')


def test_payment_update_to_another_account(client, db, data):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'])

    update_payment(client, DebtPayment.query.one().id, debt_id, amount='100', account=data['account2'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('400.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_payment_update_bank_to_cash_and_back(client, db, data):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'])
    payment_id = DebtPayment.query.one().id

    update_payment(client, payment_id, debt_id, amount='100', cash=True)

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert cash_of('DEBT PAYMENT').one().amount == Decimal('-100.00')
    assert DebtPayment.query.one().bank_account_id is None

    update_payment(client, payment_id, debt_id, amount='100', account=data['account'])

    assert balance(db, data['account']) == Decimal('900.00')
    assert cash_of('DEBT PAYMENT').count() == 0


def test_payment_update_with_more_than_the_available_money_changes_nothing(client, db, data):
    create_debt(client, amount='3000', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'])

    response = update_payment(client, DebtPayment.query.one().id, debt_id, amount='5000', account=data['account'])

    assert response.status_code == 400
    assert DebtPayment.query.one().amount == Decimal('100.00')
    assert balance(db, data['account']) == Decimal('900.00')


def test_payment_update_can_reopen_a_paid_debt(client):
    create_debt(client, amount='100', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', cash=True)
    assert only_debt().is_active is False

    update_payment(client, DebtPayment.query.one().id, debt_id, amount='40', cash=True)

    assert only_debt().is_active is True


def test_payment_update_of_a_missing_payment_is_404(client):
    create_debt(client, amount='100', cash=True)

    assert update_payment(client, 999, only_debt().id, amount='10', cash=True).status_code == 404


def test_payment_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'])
    payment_id = DebtPayment.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'update', staticmethod(boom))

    response = update_payment(client, payment_id, debt_id, amount='200', account=data['account'])

    assert response.status_code == 500
    assert DebtPayment.query.one().amount == Decimal('100.00')
    assert balance(db, data['account']) == Decimal('900.00')


def test_payment_delete_gives_the_money_back_and_reopens_the_debt(client, db, data):
    create_debt(client, amount='100', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'])
    assert only_debt().is_active is False

    response = delete_payment(client, DebtPayment.query.one().id)

    assert response.status_code == 204
    assert DebtPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert only_debt().is_active is True


def test_cash_payment_delete_removes_the_cash_ledger(client):
    create_debt(client, amount='100', cash=True)
    pay(client, only_debt().id, amount='30', cash=True)

    delete_payment(client, DebtPayment.query.one().id)

    assert DebtPayment.query.count() == 0
    assert cash_of('DEBT PAYMENT').count() == 0


def test_payment_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_debt(client, amount='300', cash=True)
    pay(client, only_debt().id, amount='100', account=data['account'])
    payment_id = DebtPayment.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(boom))

    response = delete_payment(client, payment_id)

    assert response.status_code == 500
    assert DebtPayment.query.count() == 1
    assert balance(db, data['account']) == Decimal('900.00')


def test_payment_delete_of_a_missing_payment_is_404(client):
    assert delete_payment(client, 999).status_code == 404


# ================================================================ reads

def make_debts(client, data):
    create_debt(client, amount='300', person='Carlos', description='Car repair', account=data['account'], created_at='2026-10-15T12:00')
    create_debt(client, amount='100', person='Dana', description='Old loan', cash=True, created_at='2026-09-01T12:00')


def test_debt_filter_by_time(client, data):
    make_debts(client, data)

    body = client.get('/api/debts', query_string={'start': '2026-10-01', 'end': '2026-10-31'}).get_json()

    assert [d['person_name'] for d in body['data']] == ['Carlos']
    assert body['meta']['total'] == '300.00'
    assert client.get('/api/debts', query_string={'end': '2026-10-31'}).status_code == 422  # both dates or none


def test_debt_filter_by_field(client, data):
    make_debts(client, data)

    for query, expected in (('carlos', ['Carlos']), ('old loan', ['Dana']), ('checking', ['Carlos']), ('nothing', [])):
        body = client.get('/api/debts', query_string={'q': query}).get_json()
        assert [d['person_name'] for d in body['data']] == expected, query


def test_debt_filter_understands_yes_no_active_and_paid(client, data):
    make_debts(client, data)
    update_debt(client, Debt.query.filter_by(person_name='Dana').one().id, amount='100', person='Dana',
                cash=True, paid=True, created_at='2026-09-01T12:00')

    def names(**params):
        return [d['person_name'] for d in client.get('/api/debts', query_string=params).get_json()['data']]

    assert names(q='yes') == ['Dana']
    assert names(q='no') == ['Carlos']
    assert names(q='active') == ['Carlos']
    assert names(q='paid') == ['Dana']
    assert names(q='a', start='2026-10-01', end='2026-10-31') == ['Carlos']

    meta = client.get('/api/debts', query_string={'q': 'active'}).get_json()['meta']
    assert meta['actives'] == 1 and meta['paids'] == 0
    assert meta['remaining'] == '300.00'


def test_debt_payments_of_one_debt(client):
    create_debt(client, amount='100', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='30', cash=True)

    body = client.get(f'/api/debts/{debt_id}/payments').get_json()

    assert body['meta']['count'] == 1
    assert client.get('/api/debts/999/payments').status_code == 404


def test_debt_payment_filter(client, data):
    create_debt(client, amount='300', cash=True)
    debt_id = only_debt().id
    pay(client, debt_id, amount='100', account=data['account'], created_at='2026-10-16T09:00')
    pay(client, debt_id, amount='20', cash=True, created_at='2026-09-02T09:00')

    def amounts(**params):
        response = client.get('/api/debt_payments', query_string=params)
        assert response.status_code == 200
        return sorted(float(p['amount']) for p in response.get_json()['data'])

    assert amounts(q='yes') == [20.0]
    assert amounts(q='checking') == [100.0]
    assert amounts(start='2026-10-01', end='2026-10-31') == [100.0]


def test_pages_render(client, data):
    make_debts(client, data)
    debt_id = Debt.query.filter_by(person_name='Carlos').one().id
    pay(client, debt_id, amount='10', cash=True)

    assert client.get('/debts').status_code == 200
    assert client.get(f'/debts/{debt_id}').status_code == 200
    assert client.get('/debt_payments').status_code == 200


# ------------------------------------------------------------------ in kind, and closed by hand

def test_debt_with_no_money_moved_touches_no_balance_or_ledger(client, db, data):
    response = create_debt(client, amount='80')  # not cash, no account

    assert response.status_code == 201
    assert balance(db, data['account']) == Decimal('1000.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 0


def test_debt_update_to_no_money_moved_takes_the_money_back(client, db, data):
    create_debt(client, amount='300', account=data['account'])

    update_debt(client, only_debt().id, amount='300')

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0


def test_debt_marked_as_paid_by_hand_stops_counting_as_money_to_pay(client):
    create_debt(client, amount='100', cash=True)
    assert client.get('/api/dashboard').get_json()['data']['to_pay'] == '100.00'

    update_debt(client, only_debt().id, amount='100', cash=True, paid=True)

    assert only_debt().is_active is False
    assert client.get('/api/dashboard').get_json()['data']['to_pay'] == '0.00'
    assert client.get(f'/api/debts/{only_debt().id}').get_json()['data']['remaining_amount'] == '100.00'  # still shown on the row


def test_debt_unmarked_goes_back_to_what_the_payments_say(client):
    create_debt(client, amount='100', cash=True)
    update_debt(client, only_debt().id, amount='100', cash=True, paid=True)

    update_debt(client, only_debt().id, amount='100', cash=True)

    assert only_debt().is_active is True
