"""Safety net for loans (money lent to someone) and loan payments (money coming back).

A loan takes money out of cash, a bank account or a credit card. Each payment brings money into
cash or a bank account, and the loan is "paid" (is_active False) once the payments cover it.
"""
from decimal import Decimal

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.models.loan import Loan
from app.models.loan_payment import LoanPayment

BASE = '/loans'


def loan_form(amount, person='Ana', description='Lunch money', account=None, card=None, cash=False,
              created_at='2026-10-15T12:30', paid=False):
    """The JSON body the loan form sends."""
    return {
        'amount': str(amount),
        'person_name': person,
        'description': description,
        'created_at': created_at,
        'bank_account_id': account.id if account else None,
        'credit_card_id': card.id if card else None,
        'is_cash': cash,
        'is_active': not paid,  # the edit dialog's "mark as paid" switch
    }


def payment_form(loan_id, amount, account=None, cash=False, created_at='2026-10-16T09:00'):
    return {
        'loan_id': loan_id,
        'amount': str(amount),
        'created_at': created_at,
        'bank_account_id': account.id if account else None,
        'is_cash': cash,
    }


def create_loan(client, **kwargs):
    return client.post(BASE, json=loan_form(**kwargs))


def update_loan(client, loan_id, **kwargs):
    return client.put(f'{BASE}/{loan_id}', json=loan_form(**kwargs))


def delete_loan(client, loan_id):
    return client.delete(f'{BASE}/{loan_id}')


def pay(client, loan_id, **kwargs):
    return client.post('/loan_payments', json=payment_form(loan_id, **kwargs))


def update_payment(client, payment_id, loan_id, **kwargs):
    body = payment_form(loan_id, **kwargs)
    del body['loan_id']
    return client.put(f'/loan_payments/{payment_id}', json=body)


def delete_payment(client, payment_id):
    return client.delete(f'/loan_payments/{payment_id}')


def balance(db, product):
    db.session.expire_all()
    return product.amount_available


def only_loan():
    return Loan.query.one()


def boom(*args, **kwargs):
    raise RuntimeError('ledger is down')


# ================================================================ loans: create

def test_loan_from_a_bank_account(client, db, data):
    response = create_loan(client, amount='300', account=data['account'])

    assert response.status_code == 201
    loan = only_loan()
    assert loan.code.startswith('LOAN')
    assert loan.is_active is True and loan.is_cash is False
    assert balance(db, data['account']) == Decimal('700.00')

    ledger = BankAccountTransactionsLedger.query.one()
    assert ledger.amount == Decimal('-300.00')
    assert ledger.before_update_balance == Decimal('1000.00')
    assert ledger.after_update_balance == Decimal('700.00')
    assert CashLedger.query.count() == 0 and CreditCardTransactionsLedger.query.count() == 0


def test_loan_from_a_credit_card(client, db, data):
    response = create_loan(client, amount='200', card=data['card'])

    assert response.status_code == 201
    assert balance(db, data['card']) == Decimal('600.00')
    assert CreditCardTransactionsLedger.query.one().amount == Decimal('-200.00')
    assert BankAccountTransactionsLedger.query.count() == 0


def test_loan_from_cash(client, db, data):
    response = create_loan(client, amount='80', cash=True)

    assert response.status_code == 201
    assert CashLedger.query.one().amount == Decimal('-80.00')
    assert only_loan().is_cash is True
    assert balance(db, data['account']) == Decimal('1000.00')


def test_loan_keeps_the_date_it_was_given(client):
    create_loan(client, amount='10', cash=True, created_at='2026-09-03T08:15')

    created = only_loan().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_loan_without_a_date_uses_now(client):
    response = client.post(BASE, json={'amount': '10', 'person_name': 'Ana', 'is_cash': True})

    assert response.status_code == 201
    assert only_loan().created_at is not None


def test_loan_cannot_use_a_bank_account_and_a_credit_card_together(client, db, data):
    response = create_loan(client, amount='100', account=data['account'], card=data['card'])

    assert response.status_code == 400
    assert Loan.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['card']) == Decimal('800.00')


def test_loan_with_more_than_the_available_money_changes_nothing(client, db, data):
    response = create_loan(client, amount='5000', account=data['account'])

    assert response.status_code == 400
    assert 'Insufficient' in response.get_json()['error']['message']
    assert Loan.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_loan_rejects_bad_amounts(client):
    for amount in ('0', '-5', 'abc'):
        assert create_loan(client, amount=amount, cash=True).status_code in (400, 422), amount

    assert Loan.query.count() == 0


def test_loan_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(boom))

    response = create_loan(client, amount='300', account=data['account'])

    assert response.status_code == 500
    assert Loan.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


# ================================================================ loans: update

def test_loan_update_amount_on_the_same_account(client, db, data):
    create_loan(client, amount='300', account=data['account'])

    response = update_loan(client, only_loan().id, amount='500', account=data['account'], person='Ana B')

    assert response.status_code == 200
    loan = only_loan()
    assert loan.amount == Decimal('500.00') and loan.person_name == 'Ana B'
    assert balance(db, data['account']) == Decimal('500.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('-500.00')


def test_loan_update_from_bank_account_to_credit_card(client, db, data):
    create_loan(client, amount='300', account=data['account'])

    update_loan(client, only_loan().id, amount='300', card=data['card'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['card']) == Decimal('500.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.one().amount == Decimal('-300.00')
    loan = only_loan()
    assert loan.bank_account_id is None and loan.credit_card_id == data['card'].id


def test_loan_update_to_cash_gives_the_money_back(client, db, data):
    create_loan(client, amount='300', account=data['account'])

    update_loan(client, only_loan().id, amount='300', cash=True)

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.one().amount == Decimal('-300.00')


def test_loan_update_from_cash_to_bank_account_takes_the_money(client, db, data):
    create_loan(client, amount='300', cash=True)

    update_loan(client, only_loan().id, amount='300', account=data['account'])

    assert balance(db, data['account']) == Decimal('700.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 1


def test_loan_update_with_more_than_the_available_money_changes_nothing(client, db, data):
    create_loan(client, amount='300', account=data['account'])

    response = update_loan(client, only_loan().id, amount='5000', account=data['account'])

    assert response.status_code == 400
    assert only_loan().amount == Decimal('300.00')
    assert balance(db, data['account']) == Decimal('700.00')


def test_loan_update_can_mark_it_as_paid(client):
    create_loan(client, amount='50', cash=True)

    update_loan(client, only_loan().id, amount='50', cash=True, paid=True)

    assert only_loan().is_active is False

    update_loan(client, only_loan().id, amount='50', cash=True)

    assert only_loan().is_active is True


def test_loan_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_loan(client, amount='300', account=data['account'])
    monkeypatch.setattr(BankAccountTransactionsLedger, 'update', staticmethod(boom))

    response = update_loan(client, only_loan().id, amount='400', account=data['account'])

    assert response.status_code == 500
    assert only_loan().amount == Decimal('300.00')
    assert balance(db, data['account']) == Decimal('700.00')


def test_loan_update_of_a_missing_loan_is_404(client):
    assert update_loan(client, 999, amount='10', cash=True).status_code == 404


# ================================================================ loans: delete

def test_loan_delete_gives_the_money_back_and_removes_ledgers(client, db, data):
    create_loan(client, amount='300', account=data['account'])
    create_loan(client, amount='200', card=data['card'])
    create_loan(client, amount='50', cash=True)

    for loan in Loan.query.all():
        assert delete_loan(client, loan.id).status_code == 204

    assert Loan.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['card']) == Decimal('800.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.count() == 0
    assert CashLedger.query.count() == 0


def test_loan_delete_also_undoes_its_payments(client, db, data):
    create_loan(client, amount='300', account=data['account'])
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account2'])
    pay(client, loan_id, amount='50', cash=True)

    response = delete_loan(client, loan_id)

    assert response.status_code == 204
    assert Loan.query.count() == 0 and LoanPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('500.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.count() == 0


def test_loan_without_a_bank_product_can_be_deleted(client):
    create_loan(client, amount='20')  # not cash and no bank product selected

    assert delete_loan(client, only_loan().id).status_code == 204
    assert Loan.query.count() == 0


def test_loan_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_loan(client, amount='300', account=data['account'])
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(boom))

    response = delete_loan(client, only_loan().id)

    assert response.status_code == 500
    assert Loan.query.count() == 1
    assert balance(db, data['account']) == Decimal('700.00')


def test_loan_delete_of_a_missing_loan_is_404(client):
    assert delete_loan(client, 999).status_code == 404


# ================================================================ loan payments

def test_payment_to_a_bank_account(client, db, data):
    create_loan(client, amount='300', account=data['account'])
    loan_id = only_loan().id

    response = pay(client, loan_id, amount='100', account=data['account2'])

    assert response.status_code == 201
    payment = LoanPayment.query.one()
    assert payment.code.startswith('LPMT') and payment.loan_id == loan_id
    assert balance(db, data['account2']) == Decimal('600.00')
    ledger = BankAccountTransactionsLedger.query.filter_by(reference_code=payment.code).one()
    assert ledger.amount == Decimal('100.00')
    assert ledger.after_update_balance == Decimal('600.00')
    assert only_loan().is_active is True
    assert only_loan().remaining_amount() == Decimal('200.00')


def test_cash_payment(client, db, data):
    create_loan(client, amount='300', account=data['account'])

    response = pay(client, only_loan().id, amount='100', cash=True)

    assert response.status_code == 201
    assert CashLedger.query.one().amount == Decimal('100.00')
    assert LoanPayment.query.one().bank_account_id is None


def test_loan_is_marked_as_paid_when_the_payments_cover_it(client):
    create_loan(client, amount='100', cash=True)
    loan_id = only_loan().id

    pay(client, loan_id, amount='40', cash=True)
    assert only_loan().is_active is True

    pay(client, loan_id, amount='60', cash=True)
    assert only_loan().is_active is False


def test_a_fully_paid_loan_takes_no_more_payments(client):
    create_loan(client, amount='100', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', cash=True)

    response = pay(client, loan_id, amount='10', cash=True)

    assert response.status_code == 400
    assert response.get_json()['error']['code'] == 'loan_already_paid'
    assert LoanPayment.query.count() == 1


def test_payment_for_a_missing_loan_is_404(client):
    assert pay(client, 999, amount='10', cash=True).status_code == 404


def test_payment_rejects_bad_amounts_and_a_missing_account(client, data):
    create_loan(client, amount='300', cash=True)
    loan_id = only_loan().id

    for amount in ('0', '-5', 'abc'):
        assert pay(client, loan_id, amount=amount, cash=True).status_code in (400, 422), amount
    assert pay(client, loan_id, amount='10').status_code == 400  # not cash and no account

    assert LoanPayment.query.count() == 0


def test_payment_keeps_the_date_it_was_given(client):
    create_loan(client, amount='300', cash=True)

    pay(client, only_loan().id, amount='10', cash=True, created_at='2026-09-03T08:15')

    created = LoanPayment.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_payment_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_loan(client, amount='300', cash=True)
    monkeypatch.setattr(BankAccountTransactionsLedger, 'create', staticmethod(boom))

    response = pay(client, only_loan().id, amount='100', account=data['account'])

    assert response.status_code == 500
    assert LoanPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_payment_update_amount_on_the_same_account(client, db, data):
    create_loan(client, amount='300', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account'])
    payment_id = LoanPayment.query.one().id

    response = update_payment(client, payment_id, loan_id, amount='250', account=data['account'])

    assert response.status_code == 200
    assert LoanPayment.query.one().amount == Decimal('250.00')
    assert balance(db, data['account']) == Decimal('1250.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('250.00')


def test_payment_update_to_another_account(client, db, data):
    create_loan(client, amount='300', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account'])

    update_payment(client, LoanPayment.query.one().id, loan_id, amount='100', account=data['account2'])

    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('600.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_payment_update_bank_to_cash_and_back(client, db, data):
    create_loan(client, amount='300', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account'])
    payment_id = LoanPayment.query.one().id

    update_payment(client, payment_id, loan_id, amount='100', cash=True)

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CashLedger.query.filter(CashLedger.type == 'LOAN PAYMENT').one().amount == Decimal('100.00')

    update_payment(client, payment_id, loan_id, amount='100', account=data['account'])

    assert balance(db, data['account']) == Decimal('1100.00')
    assert CashLedger.query.filter(CashLedger.type == 'LOAN PAYMENT').count() == 0


def test_payment_update_can_reopen_a_paid_loan(client):
    create_loan(client, amount='100', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', cash=True)
    assert only_loan().is_active is False

    update_payment(client, LoanPayment.query.one().id, loan_id, amount='40', cash=True)

    assert only_loan().is_active is True


def test_payment_update_of_a_missing_payment_is_404(client):
    create_loan(client, amount='100', cash=True)

    assert update_payment(client, 999, only_loan().id, amount='10', cash=True).status_code == 404


def test_payment_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_loan(client, amount='300', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account'])
    payment_id = LoanPayment.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'update', staticmethod(boom))

    response = update_payment(client, payment_id, loan_id, amount='200', account=data['account'])

    assert response.status_code == 500
    assert LoanPayment.query.one().amount == Decimal('100.00')
    assert balance(db, data['account']) == Decimal('1100.00')


def test_payment_delete_takes_the_money_back_and_reopens_the_loan(client, db, data):
    create_loan(client, amount='100', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account'])
    payment_id = LoanPayment.query.one().id
    assert only_loan().is_active is False

    response = delete_payment(client, payment_id)

    assert response.status_code == 204
    assert LoanPayment.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert only_loan().is_active is True


def test_cash_payment_delete_removes_the_cash_ledger(client):
    create_loan(client, amount='100', account=None, cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='30', cash=True)

    delete_payment(client, LoanPayment.query.one().id)

    assert LoanPayment.query.count() == 0
    assert CashLedger.query.filter(CashLedger.type == 'LOAN PAYMENT').count() == 0


def test_payment_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    create_loan(client, amount='300', cash=True)
    pay(client, only_loan().id, amount='100', account=data['account'])
    payment_id = LoanPayment.query.one().id
    monkeypatch.setattr(BankAccountTransactionsLedger, 'delete', staticmethod(boom))

    response = delete_payment(client, payment_id)

    assert response.status_code == 500
    assert LoanPayment.query.count() == 1
    assert balance(db, data['account']) == Decimal('1100.00')


def test_payment_delete_of_a_missing_payment_is_404(client):
    assert delete_payment(client, 999).status_code == 404


# ================================================================ reads

def make_loans(client, data):
    create_loan(client, amount='300', person='Ana', description='Rent help', account=data['account'], created_at='2026-10-15T12:00')
    create_loan(client, amount='100', person='Beto', description='Old debt', cash=True, created_at='2026-09-01T12:00')


def test_loan_filter_by_time(client, data):
    make_loans(client, data)

    body = client.get(BASE, query_string={'start': '2026-10-01', 'end': '2026-10-31'}).get_json()

    assert [l['person_name'] for l in body['data']] == ['Ana']
    assert body['meta']['total'] == '300.00'
    assert client.get(BASE, query_string={'start': '2026-10-01'}).status_code == 422  # both dates or none


def test_loan_filter_by_field(client, data):
    make_loans(client, data)

    for query, expected in (('ana', ['Ana']), ('old debt', ['Beto']), ('checking', ['Ana']), ('nothing', [])):
        body = client.get(BASE, query_string={'q': query}).get_json()
        assert [l['person_name'] for l in body['data']] == expected, query


def test_loan_filter_understands_yes_no_active_and_paid(client, data):
    make_loans(client, data)
    update_loan(client, Loan.query.filter_by(person_name='Beto').one().id, amount='100', person='Beto', cash=True, paid=True, created_at='2026-09-01T12:00')

    def names(**params):
        return [l['person_name'] for l in client.get(BASE, query_string=params).get_json()['data']]

    assert names(q='yes') == ['Beto']
    assert names(q='no') == ['Ana']
    assert names(q='active') == ['Ana']
    assert names(q='paid') == ['Beto']
    assert names(q='a', start='2026-10-01', end='2026-10-31') == ['Ana']

    meta = client.get(BASE, query_string={'q': 'active'}).get_json()['meta']
    assert meta['actives'] == 1 and meta['paids'] == 0
    assert meta['remaining'] == '300.00'


def test_loan_payments_of_one_loan(client):
    create_loan(client, amount='100', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='30', cash=True)

    body = client.get(f'{BASE}/{loan_id}/payments').get_json()

    assert body['meta']['count'] == 1
    assert client.get(f'{BASE}/999/payments').status_code == 404


def test_loan_payment_filter(client, data):
    create_loan(client, amount='300', cash=True)
    loan_id = only_loan().id
    pay(client, loan_id, amount='100', account=data['account'], created_at='2026-10-16T09:00')
    pay(client, loan_id, amount='20', cash=True, created_at='2026-09-02T09:00')

    def amounts(**params):
        response = client.get('/loan_payments', query_string=params)
        assert response.status_code == 200
        return sorted(float(p['amount']) for p in response.get_json()['data'])

    assert amounts(q='yes') == [20.0]
    assert amounts(q='checking') == [100.0]
    assert amounts(q='x', start='2026-10-01', end='2026-10-31') == []
    assert amounts(start='2026-10-01', end='2026-10-31') == [100.0]


def test_a_loan_can_be_read_one_by_one(client):
    create_loan(client, amount='100', cash=True)
    loan_id = only_loan().id

    assert client.get(f'{BASE}/{loan_id}').get_json()['data']['person_name'] == 'Ana'
    assert client.get(f'{BASE}/999').status_code == 404


def test_pages_render(client, data):
    make_loans(client, data)
    loan_id = Loan.query.filter_by(person_name='Ana').one().id
    pay(client, loan_id, amount='10', cash=True)

    assert client.get(f'{BASE}/index').status_code == 200
    assert client.get(f'{BASE}/associated_records/{loan_id}').status_code == 200
    assert client.get('/loan_payments/index').status_code == 200


# ------------------------------------------------------------------ in kind, and closed by hand

def test_loan_with_no_money_moved_touches_no_balance_or_ledger(client, db, data):
    response = create_loan(client, amount='80')  # not cash, no account, no card

    assert response.status_code == 201
    assert balance(db, data['account']) == Decimal('1000.00')
    assert CashLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.count() == 0


def test_loan_update_to_no_money_moved_gives_the_money_back(client, db, data):
    create_loan(client, amount='300', account=data['account'])

    update_loan(client, only_loan().id, amount='300')

    assert balance(db, data['account']) == Decimal('1000.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert only_loan().bank_account_id is None


def test_loan_marked_as_paid_by_hand_stops_counting_as_money_to_collect(client):
    create_loan(client, amount='100', cash=True)
    assert client.get('/dashboard').get_json()['data']['to_collect'] == '100.00'

    client.post('/loan_payments', json=payment_form(only_loan().id, '30', cash=True))
    update_loan(client, only_loan().id, amount='100', cash=True, paid=True)

    loan = only_loan()
    assert loan.is_active is False
    assert client.get('/dashboard').get_json()['data']['to_collect'] == '0.00'
    assert client.get(f'{BASE}/{loan.id}').get_json()['data']['remaining_amount'] == '70.00'  # still shown on the row


def test_loan_unmarked_goes_back_to_what_the_payments_say(client):
    create_loan(client, amount='100', cash=True)
    update_loan(client, only_loan().id, amount='100', cash=True, paid=True)

    update_loan(client, only_loan().id, amount='100', cash=True)  # switch off, nothing paid yet

    assert only_loan().is_active is True

    client.post('/loan_payments', json=payment_form(only_loan().id, '100', cash=True))
    update_loan(client, only_loan().id, amount='100', cash=True)  # fully paid by payments

    assert only_loan().is_active is False
