"""Safety net for bank transfers and credit card payments.

bank transfer         origin account -> destination account (two ledger rows, one per account)
credit card payment   bank account -> credit card (gives the card its available credit back),
                      or a "cashback" payment that adds credit to the card without touching any account
"""
from decimal import Decimal

import pytest

from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.banktransfer import BankTransfer
from app.models.credit_card_payment import CreditCardPayment
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger


def balance(db, product):
    db.session.expire_all()
    return product.amount_available


def boom(*args, **kwargs):
    raise RuntimeError('ledger is down')


# ================================================================ bank transfers

def transfer_form(amount, origin, destination, created_at='2026-10-15T12:30'):
    return {
        'amount': str(amount),
        'from_bank_account_id': origin.id if origin else None,
        'to_bank_account_id': destination.id if destination else None,
        'created_at': created_at,
    }


def make_transfer(client, amount, origin, destination, **kwargs):
    return client.post('/api/bank_transfers', json=transfer_form(amount, origin, destination, **kwargs))


def change_transfer(client, transfer_id, amount, origin, destination, **kwargs):
    return client.put(f'/api/bank_transfers/{transfer_id}', json=transfer_form(amount, origin, destination, **kwargs))


def remove_transfer(client, transfer_id):
    return client.delete(f'/api/bank_transfers/{transfer_id}')


def test_transfer_moves_money_and_writes_two_ledger_rows(client, db, data):
    response = make_transfer(client, '300', data['account'], data['account2'])

    assert response.status_code == 201
    transfer = BankTransfer.query.one()
    assert transfer.code.startswith('BTRA')
    assert balance(db, data['account']) == Decimal('700.00')
    assert balance(db, data['account2']) == Decimal('800.00')

    out, incoming = sorted(BankAccountTransactionsLedger.query.all(), key=lambda row: row.amount)
    assert out.amount == Decimal('-300.00') and out.bank_account_id == data['account'].id
    assert out.before_update_balance == Decimal('1000.00') and out.after_update_balance == Decimal('700.00')
    assert incoming.amount == Decimal('300.00') and incoming.bank_account_id == data['account2'].id
    assert incoming.before_update_balance == Decimal('500.00') and incoming.after_update_balance == Decimal('800.00')
    assert out.reference_code == incoming.reference_code == transfer.code


def test_transfer_keeps_the_date_it_was_given(client, data):
    make_transfer(client, '10', data['account'], data['account2'], created_at='2026-09-03T08:15')

    created = BankTransfer.query.one().created_at
    assert (created.year, created.month, created.day) == (2026, 9, 3)


def test_transfer_without_a_date_uses_now(client, data):
    response = client.post('/api/bank_transfers', json={
        'amount': '10', 'from_bank_account_id': data['account'].id, 'to_bank_account_id': data['account2'].id})

    assert response.status_code == 201
    assert BankTransfer.query.one().created_at is not None


def test_transfer_with_more_than_the_available_money_changes_nothing(client, db, data):
    response = make_transfer(client, '5000', data['account'], data['account2'])

    assert response.status_code == 400
    assert BankTransfer.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('500.00')


def test_transfer_rejects_bad_amounts_missing_and_equal_accounts(client, db, data):
    for amount in ('0', '-5', 'abc'):
        assert make_transfer(client, amount, data['account'], data['account2']).status_code in (400, 422), amount

    assert make_transfer(client, '10', None, data['account2']).status_code == 422
    assert make_transfer(client, '10', data['account'], None).status_code == 422
    assert make_transfer(client, '10', data['account'], data['account']).status_code == 400

    assert BankTransfer.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')


def test_transfer_create_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    monkeypatch.setattr(BankAccountTransactionsLedger, '_create_ledger_for_bank_transfer', staticmethod(boom))

    response = make_transfer(client, '300', data['account'], data['account2'])

    assert response.status_code == 500
    assert BankTransfer.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('500.00')


def test_transfer_update_amount(client, db, data):
    make_transfer(client, '300', data['account'], data['account2'])

    response = change_transfer(client, BankTransfer.query.one().id, '100', data['account'], data['account2'])

    assert response.status_code == 200
    assert BankTransfer.query.one().amount == Decimal('100.00')
    assert balance(db, data['account']) == Decimal('900.00')
    assert balance(db, data['account2']) == Decimal('600.00')
    assert sorted(row.amount for row in BankAccountTransactionsLedger.query.all()) == [Decimal('-100.00'), Decimal('100.00')]


def test_transfer_update_to_another_destination(client, db, data):
    make_transfer(client, '300', data['account'], data['account2'])
    third = type(data['account'])(nick_name='Third', amount_available=Decimal('0.00'), bank_id=data['bank'].id)
    db.session.add(third)
    db.session.commit()

    response = change_transfer(client, BankTransfer.query.one().id, '300', data['account'], third)

    assert response.status_code == 200
    assert balance(db, data['account']) == Decimal('700.00')
    assert balance(db, data['account2']) == Decimal('500.00')
    assert balance(db, third) == Decimal('300.00')
    incoming = BankAccountTransactionsLedger.query.filter(BankAccountTransactionsLedger.amount > 0).one()
    assert incoming.bank_account_id == third.id


def test_transfer_update_is_refused_when_the_destination_spent_the_money(client, db, data):
    make_transfer(client, '300', data['account'], data['account2'])
    make_transfer(client, '750', data['account2'], data['account'])  # account2 now has 50

    first = BankTransfer.query.order_by(BankTransfer.id).first()
    response = change_transfer(client, first.id, '100', data['account'], data['account2'])

    assert response.status_code == 400
    assert BankTransfer.query.order_by(BankTransfer.id).first().amount == Decimal('300.00')
    assert balance(db, data['account2']) == Decimal('50.00')


def test_transfer_update_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    make_transfer(client, '300', data['account'], data['account2'])
    monkeypatch.setattr(BankAccountTransactionsLedger, '_update_ledger_for_bank_transfer', staticmethod(boom))

    response = change_transfer(client, BankTransfer.query.one().id, '100', data['account'], data['account2'])

    assert response.status_code == 500
    assert BankTransfer.query.one().amount == Decimal('300.00')
    assert balance(db, data['account']) == Decimal('700.00')
    assert balance(db, data['account2']) == Decimal('800.00')


def test_transfer_update_of_a_missing_transfer_is_404(client, data):
    assert change_transfer(client, 999, '10', data['account'], data['account2']).status_code == 404


def test_transfer_delete_sends_the_money_back_and_removes_both_ledger_rows(client, db, data):
    make_transfer(client, '300', data['account'], data['account2'])

    response = remove_transfer(client, BankTransfer.query.one().id)

    assert response.status_code == 204
    assert BankTransfer.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 0
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('500.00')


def test_transfer_delete_is_refused_when_the_destination_spent_the_money(client, db, data):
    make_transfer(client, '300', data['account'], data['account2'])
    make_transfer(client, '750', data['account2'], data['account'])

    first = BankTransfer.query.order_by(BankTransfer.id).first()
    response = remove_transfer(client, first.id)

    assert response.status_code == 400
    assert BankTransfer.query.count() == 2


def test_transfer_delete_is_all_or_nothing_when_the_ledger_fails(client, db, data, monkeypatch):
    make_transfer(client, '300', data['account'], data['account2'])
    monkeypatch.setattr(BankAccountTransactionsLedger, '_delete_ledger_for_bank_transfer', staticmethod(boom))

    response = remove_transfer(client, BankTransfer.query.one().id)

    assert response.status_code == 500
    assert BankTransfer.query.count() == 1
    assert balance(db, data['account']) == Decimal('700.00')
    assert balance(db, data['account2']) == Decimal('800.00')


def test_transfer_delete_of_a_missing_transfer_is_404(client):
    assert remove_transfer(client, 999).status_code == 404


def test_transfer_get_record(client, data):
    make_transfer(client, '300', data['account'], data['account2'])

    body = client.get(f'/api/bank_transfers/{BankTransfer.query.one().id}').get_json()['data']

    assert body['from_bank_account_name'] == 'Checking'
    assert body['to_bank_account_name'] == 'Savings'
    assert client.get('/api/bank_transfers/999').status_code == 404


# ================================================================ credit card payments
#
# Credit card payments go through app/services/credit_card_payment_service.py.

def card_payment_form(amount, card, account=None, cashback=False):
    return {
        'amount': str(amount),
        'credit_card_id': card.id,
        'bank_account_id': account.id if account else None,
        'is_cashback': cashback,
    }


def pay_card(client, amount, card, account=None, cashback=False):
    return client.post('/api/credit_card_payments', json=card_payment_form(amount, card, account, cashback))


def test_card_payment_from_a_bank_account(client, db, data):
    response = pay_card(client, '200', data['card'], data['account'])

    assert response.status_code == 201
    payment = CreditCardPayment.query.one()
    assert payment.code.startswith('CCP') and payment.is_cashback is False
    assert balance(db, data['card']) == Decimal('1000.00')
    assert balance(db, data['account']) == Decimal('800.00')
    assert CreditCardTransactionsLedger.query.one().amount == Decimal('200.00')
    assert BankAccountTransactionsLedger.query.one().amount == Decimal('-200.00')


def test_cashback_payment_adds_credit_without_touching_an_account(client, db, data):
    response = pay_card(client, '50', data['card'], cashback=True)

    assert response.status_code == 201
    assert CreditCardPayment.query.one().is_cashback is True
    assert balance(db, data['card']) == Decimal('850.00')
    assert balance(db, data['account']) == Decimal('1000.00')
    assert CreditCardTransactionsLedger.query.one().amount == Decimal('50.00')
    assert BankAccountTransactionsLedger.query.count() == 0


def test_card_payment_with_more_than_the_available_money_changes_nothing(client, db, data):
    response = pay_card(client, '5000', data['card'], data['account'])

    assert response.status_code == 400
    assert CreditCardPayment.query.count() == 0
    assert balance(db, data['card']) == Decimal('800.00')
    assert balance(db, data['account']) == Decimal('1000.00')


def test_card_payment_rejects_bad_amounts_and_a_missing_account(client, db, data):
    for amount in ('0', '-5', 'abc'):
        assert pay_card(client, amount, data['card'], data['account']).status_code in (400, 422), amount
    assert pay_card(client, '10', data['card']).status_code == 400  # no account and not cashback

    assert CreditCardPayment.query.count() == 0
    assert balance(db, data['card']) == Decimal('800.00')


def test_card_payment_update_amount(client, db, data):
    pay_card(client, '200', data['card'], data['account'])
    payment_id = CreditCardPayment.query.one().id

    response = client.put(f'/api/credit_card_payments/{payment_id}', json=card_payment_form('300', data['card'], data['account']))

    assert response.status_code == 200
    assert CreditCardPayment.query.one().amount == Decimal('300.00')
    assert balance(db, data['card']) == Decimal('1100.00')
    assert balance(db, data['account']) == Decimal('700.00')


def test_card_payment_delete_undoes_it(client, db, data):
    pay_card(client, '200', data['card'], data['account'])
    payment_id = CreditCardPayment.query.one().id

    response = client.delete(f'/api/credit_card_payments/{payment_id}')

    assert response.status_code == 204
    assert CreditCardPayment.query.count() == 0
    assert balance(db, data['card']) == Decimal('800.00')
    assert balance(db, data['account']) == Decimal('1000.00')
    assert CreditCardTransactionsLedger.query.count() == 0
    assert BankAccountTransactionsLedger.query.count() == 0


def test_cashback_payment_delete_undoes_it(client, db, data):
    pay_card(client, '50', data['card'], cashback=True)
    payment_id = CreditCardPayment.query.one().id

    response = client.delete(f'/api/credit_card_payments/{payment_id}')

    assert response.status_code == 204
    assert balance(db, data['card']) == Decimal('800.00')
    assert CreditCardTransactionsLedger.query.count() == 0


def test_card_payment_update_to_cashback_returns_the_old_amount_to_the_account(client, db, data):
    pay_card(client, '200', data['card'], data['account'])
    payment_id = CreditCardPayment.query.one().id

    response = client.put(f'/api/credit_card_payments/{payment_id}', json=card_payment_form('300', data['card'], cashback=True))

    assert response.status_code == 200
    payment = CreditCardPayment.query.one()
    assert payment.is_cashback is True and payment.bank_account_id is None
    assert balance(db, data['account']) == Decimal('1000.00')  # the 200 came back, nothing else
    assert balance(db, data['card']) == Decimal('1100.00')
    assert BankAccountTransactionsLedger.query.count() == 0
    assert CreditCardTransactionsLedger.query.one().amount == Decimal('300.00')


def test_card_payment_update_to_another_account(client, db, data):
    pay_card(client, '200', data['card'], data['account'])
    payment_id = CreditCardPayment.query.one().id

    response = client.put(f'/api/credit_card_payments/{payment_id}', json=card_payment_form('200', data['card'], data['account2']))

    assert response.status_code == 200
    assert balance(db, data['account']) == Decimal('1000.00')
    assert balance(db, data['account2']) == Decimal('300.00')
    assert BankAccountTransactionsLedger.query.one().bank_account_id == data['account2'].id


def test_card_payment_update_without_funds_changes_nothing(client, db, data):
    pay_card(client, '200', data['card'], data['account'])
    payment_id = CreditCardPayment.query.one().id

    response = client.put(f'/api/credit_card_payments/{payment_id}', json=card_payment_form('5000', data['card'], data['account']))

    assert response.status_code == 400
    assert CreditCardPayment.query.one().amount == Decimal('200.00')
    assert balance(db, data['account']) == Decimal('800.00')
    assert balance(db, data['card']) == Decimal('1000.00')


def test_card_payment_missing_records_answer_404(client, db, data):
    assert client.put('/api/credit_card_payments/999', json=card_payment_form('10', data['card'], data['account'])).status_code == 404
    assert client.delete('/api/credit_card_payments/999').status_code == 404


def test_card_payment_accepts_a_created_at_date(client, db, data):
    form = card_payment_form('20', data['card'], data['account'])
    form['created_at'] = '2026-03-05T10:30'

    created = client.post('/api/credit_card_payments', json=form)

    assert created.status_code == 201
    assert created.get_json()['data']['created_at'] == '2026-03-05T10:30:00'  # local time out, UTC in the database
