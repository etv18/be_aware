"""Bank accounts: JSON in, service call, JSON out; plus what hangs from an account and its reports."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource, data, year_param
from app.models.bank_account import BankAccount
from app.services import bank_account_service

RESOURCE = Resource(
    label='Bank account', model=BankAccount, serialize=ser.bank_account, has_amount=False,
    create_schema=schemas.BankAccountIn, create=bank_account_service.create_bank_account,
    update=bank_account_service.update_bank_account, delete=bank_account_service.delete_bank_account,
    default_list=bank_account_service.list_visible,
)


def records_of(account_id):
    """Every record that touched the account, grouped by kind: {"expenses": [...], "deposits": [...]}"""
    account = bank_account_service.get_bank_account(account_id)
    records = ser.group_by_table(
        account.expenses, account.incomes, account.loans, account.loan_payments, account.credit_card_payments,
        account.withdrawals, account.debts, account.debt_payments, account.deposits,
        bank_account_service.transfers_of(account),
    )
    return data({'bank_account': ser.bank_account(account), 'records': records})


def yearly_report(account_id):
    bank_account_service.get_bank_account(account_id)
    return data(bank_account_service.yearly_total_per_association(account_id, year_param()))


def cash_flow_report(account_id):
    bank_account_service.get_bank_account(account_id)
    return data(bank_account_service.cash_flow(account_id, year_param()))


def monthly_report(account_id):
    bank_account_service.get_bank_account(account_id)
    return data(bank_account_service.monthly_total_per_association(account_id))
