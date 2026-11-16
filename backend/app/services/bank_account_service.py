"""Business rules and reports for bank accounts."""
from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.banktransfer import BankTransfer
from app.models.credit_card_payment import CreditCardPayment
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.models.deposit import Deposit
from app.models.expense import Expense
from app.models.income import Income
from app.models.loan import Loan
from app.models.loan_payment import LoanPayment
from app.models.withdrawal import Withdrawal
from app.services import associations, money
from app.utils.bank_accounts.filter_data import (
    get_monthly_total_amount_info,
    get_monthly_total_amount_info_of_transfers,
    get_yearly_total_amount_info,
    get_yearly_total_amount_info_of_transfers,
)
from app.utils.date_handling import MONTHS
from app.utils.filter_data import get_not_deleted_records
from app.utils.transactions import atomic

OUTGOING_MODELS = (Expense, Withdrawal, Loan, CreditCardPayment, DebtPayment)
INCOMING_MODELS = (LoanPayment, Income, Deposit, Debt)
ALL_MODELS = OUTGOING_MODELS + INCOMING_MODELS


# ------------------------------------------------------------------ writes

def create_bank_account(*, nick_name, amount_available, account_number, bank_id):
    amount_available = money.validate_amount(amount_available)

    with atomic():
        bank_account = BankAccount(
            nick_name=nick_name,
            amount_available=amount_available,
            account_number=account_number,
            bank_id=bank_id,
        )
        db.session.add(bank_account)

    return bank_account


def update_bank_account(account_id, *, nick_name, account_number, amount_available, bank_id):
    amount_available = money.validate_amount(amount_available)

    with atomic():
        bank_account = money.get_record(BankAccount, account_id, 'Bank account')
        bank_account.nick_name = nick_name
        bank_account.account_number = account_number
        bank_account.amount_available = amount_available
        bank_account.bank_id = bank_id

    return bank_account


def delete_bank_account(account_id):
    """Bank accounts are hidden, not removed, so their history stays readable."""
    with atomic():
        money.get_record(BankAccount, account_id, 'Bank account').is_deleted = True


# ------------------------------------------------------------------ reads

def list_visible():
    return get_not_deleted_records(model=BankAccount)


def get_bank_account(account_id):
    return money.get_record(BankAccount, account_id, 'Bank account')


def transfers_of(bank_account):
    """Transfers that left or reached the account, newest first."""
    return (
        BankTransfer.query
        .filter((BankTransfer.from_bank_account_id == bank_account.id) | (BankTransfer.to_bank_account_id == bank_account.id))
        .order_by(BankTransfer.created_at.desc())
        .all()
    )


def associated_records_page(account_id):
    """What the account's detail page needs."""
    bank_account = get_bank_account(account_id)

    return {
        'bank_account': bank_account,
        'all_bank_accounts': BankAccount.query.all(),
        'banktransfers': transfers_of(bank_account),
    }


def associated_records(account_id):
    """{'owner_bank_account_id': id, 'records': {table name: [record dicts]}}."""
    bank_account = get_bank_account(account_id)

    records = associations.group_by_table(
        bank_account.expenses,
        bank_account.incomes,
        bank_account.loans,
        bank_account.loan_payments,
        bank_account.credit_card_payments,
        bank_account.withdrawals,
        bank_account.debts,
        bank_account.debt_payments,
        bank_account.deposits,
        transfers_of(bank_account),
    )
    return {'owner_bank_account_id': bank_account.id, 'records': records}


def cash_flow(bank_account_id, year=None):
    """Money in and out of the account for each month of the year, and the balance of each month."""
    transfers = get_yearly_total_amount_info_of_transfers(id=bank_account_id, year=year)

    outgoings = _sum_by_month(bank_account_id, OUTGOING_MODELS, transfers['outgoings'], year)
    incomings = _sum_by_month(bank_account_id, INCOMING_MODELS, transfers['incomings'], year)

    return {
        'months': MONTHS,
        'outgoings': outgoings,
        'incomings': incomings,
        'balances': [incoming - outgoing for incoming, outgoing in zip(incomings, outgoings)],
    }


def yearly_total_per_association(bank_account_id, year=None):
    """For each kind of record, what it moved through the account in each month of the year."""
    transfers = get_yearly_total_amount_info_of_transfers(id=bank_account_id, year=year)

    info = {
        model.__tablename__: get_yearly_total_amount_info(id=bank_account_id, CustomModel=model, year=year)
        for model in ALL_MODELS
    }
    info['outgoing_transfers'] = transfers['outgoings']
    info['incoming_transfers'] = transfers['incomings']

    return {'months': MONTHS, 'associations_info': info}


def monthly_total_per_association(bank_account_id):
    """The same, for the current month only."""
    now = datetime.now()

    totals = {
        model.__tablename__: get_monthly_total_amount_info(id=bank_account_id, CustomModel=model, year=now.year, month=now.month)
        for model in ALL_MODELS
    }
    transfers = get_monthly_total_amount_info_of_transfers(id=bank_account_id, year=now.year, month=now.month)
    totals['transfers_incomings'] = transfers['incomings']
    totals['transfers_outgoings'] = transfers['outgoings']

    return {'monthly_totals': totals}


def _sum_by_month(bank_account_id, models, transfers, year):
    """Add up the monthly totals of several models plus the transfers list."""
    totals = [Decimal('0.00')] * 12
    for monthly in [get_yearly_total_amount_info(id=bank_account_id, CustomModel=m, year=year) for m in models] + [transfers]:
        totals = [total + month for total, month in zip(totals, monthly)]
    return totals
