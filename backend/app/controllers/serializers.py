"""How each record looks in a JSON response.

Rules every serializer follows:
  * money is a string with two decimals ("1234.50"), never a float
  * `created_at` / `updated_at` are local wall-clock ISO text (see times.py)
  * a related record contributes its id and its readable name (`bank_account_id`, `bank_account_name`)
"""
from decimal import Decimal

from app.utils.times import to_local_iso


def money(value):
    if value is None:
        return None
    return f'{Decimal(value):.2f}'


def _name(related, attribute='nick_name'):
    return getattr(related, attribute, None) if related is not None else None


def _stamps(record, stored_as_utc=True):
    return {
        'created_at': to_local_iso(record.created_at, stored_as_utc),
        'updated_at': to_local_iso(getattr(record, 'updated_at', None), stored_as_utc),
    }


# ------------------------------------------------------------------ money in and out

def expense(e):
    return {
        'id': e.id,
        'code': e.code,
        'amount': money(e.amount),
        'is_cash': bool(e.is_cash),
        'description': e.description,
        'expense_category_id': e.expense_category_id,
        'expense_category_name': _name(e.expense_category, 'name').title() if e.expense_category else None,
        'credit_card_id': e.credit_card_id,
        'credit_card_name': _name(e.credit_card),
        'bank_account_id': e.bank_account_id,
        'bank_account_name': _name(e.bank_account),
        **_stamps(e, stored_as_utc=False),
    }


def income(i):
    return {
        'id': i.id,
        'code': i.code,
        'amount': money(i.amount),
        'is_cash': bool(i.is_cash),
        'description': i.description,
        'bank_account_id': i.bank_account_id,
        'bank_account_name': _name(i.bank_account),
        **_stamps(i, stored_as_utc=False),
    }


def _cash_movement(record):
    """Withdrawals and deposits: money between cash and one bank account."""
    return {
        'id': record.id,
        'code': record.code,
        'amount': money(record.amount),
        'description': record.description,
        'bank_account_id': record.bank_account_id,
        'bank_account_name': _name(record.bank_account),
        **_stamps(record),
    }


withdrawal = _cash_movement
deposit = _cash_movement


def banktransfer(t):
    return {
        'id': t.id,
        'code': t.code,
        'amount': money(t.amount),
        'from_bank_account_id': t.from_bank_account_id,
        'from_bank_account_name': _name(t.from_bank_account),
        'to_bank_account_id': t.to_bank_account_id,
        'to_bank_account_name': _name(t.to_bank_account),
        **_stamps(t),
    }


def credit_card_payment(p):
    return {
        'id': p.id,
        'code': p.code,
        'amount': money(p.amount),
        'is_cashback': bool(p.is_cashback),
        'credit_card_id': p.credit_card_id,
        'credit_card_name': _name(p.credit_card),
        'bank_account_id': p.bank_account_id,
        'bank_account_name': _name(p.bank_account),
        **_stamps(p),
    }


# ------------------------------------------------------------------ loans and debts

def _obligation(record):
    total_paid = record.total_payments()
    return {
        'id': record.id,
        'code': getattr(record, 'code', None),
        'person_name': record.person_name,
        'amount': money(record.amount),
        'is_cash': bool(record.is_cash),
        'is_active': bool(record.is_active),
        'status': 'active' if record.is_active else 'paid',
        'description': record.description,
        'bank_account_id': record.bank_account_id,
        'bank_account_name': _name(record.bank_account),
        'total_paid': money(total_paid),
        'remaining_amount': money(record.remaining_amount()),
        **_stamps(record),
    }


def loan(record):
    return {**_obligation(record), 'credit_card_id': record.credit_card_id, 'credit_card_name': _name(record.credit_card)}


debt = _obligation


def _payment(record, parent_key):
    return {
        'id': record.id,
        'code': record.code,
        'amount': money(record.amount),
        'is_cash': bool(record.is_cash),
        parent_key: getattr(record, parent_key),
        'person_name': _name(getattr(record, parent_key[:-3]), 'person_name'),
        'bank_account_id': record.bank_account_id,
        'bank_account_name': _name(record.bank_account),
        **_stamps(record),
    }


def loan_payment(p):
    return _payment(p, 'loan_id')


def debt_payment(p):
    return _payment(p, 'debt_id')


# ------------------------------------------------------------------ products and reference data

def bank(b):
    return {'id': b.id, 'name': b.name, **_stamps(b)}


def bank_account(a):
    return {
        'id': a.id,
        'nick_name': a.nick_name,
        'account_number': a.account_number,
        'amount_available': money(a.amount_available),
        'is_active': bool(a.is_active),
        'bank_id': a.bank_id,
        'bank_name': _name(a.bank, 'name'),
        **_stamps(a),
    }


def credit_card(c):
    return {
        'id': c.id,
        'nick_name': c.nick_name,
        'limit': money(c.limit),
        'amount_available': money(c.amount_available),
        'used': money(c.limit - c.amount_available),
        'is_active': bool(c.is_active),
        'bank_id': c.bank_id,
        'bank_name': _name(c.bank, 'name'),
        **_stamps(c),
    }


def expense_category(c):
    return {'id': c.id, 'name': c.name, 'display_name': c.name.title(), 'limit': money(c.limit), **_stamps(c)}


# ------------------------------------------------------------------ ledgers

def cash_ledger(row):
    return {
        'id': row.id,
        'reference_code': row.reference_code,
        'type': row.type,
        'amount': money(row.amount),
        'is_adjustment': (row.type or '').upper() == 'ADJUSTMENT',
        **_stamps(row),
    }


def _product_ledger(row):
    return {
        'id': row.id,
        'reference_code': row.reference_code,
        'transaction_type': row.transaction_type,
        'amount': money(row.amount),
        'before_balance': money(row.before_update_balance),
        'after_balance': money(row.after_update_balance),
        **_stamps(row),
    }


def bank_ledger(row):
    return {**_product_ledger(row), 'bank_account_id': row.bank_account_id, 'bank_account_name': _name(row.bank_account)}


def card_ledger(row):
    return {**_product_ledger(row), 'credit_card_id': row.credit_card_id, 'credit_card_name': _name(row.credit_card)}


# ------------------------------------------------------------------ record groups (a table name -> its rows)

BY_TABLE = {
    'expenses': expense,
    'incomes': income,
    'withdrawals': withdrawal,
    'deposits': deposit,
    'loans': loan,
    'loan_payment': loan_payment,  # (sic) the table is called loan_payment
    'debts': debt,
    'debt_payments': debt_payment,
    'credit_card_payments': credit_card_payment,
    'bank_transfers': banktransfer,
}


RENAMED = {'loan_payment': 'loan_payments'}


def group_by_table(*record_lists):
    """{'expenses': [...], 'loan_payments': [...]} for every list that has rows."""
    grouped = {}
    for records in record_lists:
        if records:
            table = records[0].__class__.__tablename__
            grouped[RENAMED.get(table, table)] = [BY_TABLE[table](r) for r in records]
    return grouped
