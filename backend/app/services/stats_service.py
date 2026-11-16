"""Yearly and monthly reports over every kind of money record. Read only."""
from datetime import datetime
from decimal import Decimal

import app.utils.bank_transactional_classes as btc
import app.utils.cash_transactional_classes as ctc
from app.utils.date_handling import MONTHS
from app.utils.filter_data import (
    get_monthly_total_amount_info,
    get_yearly_total_amount_info,
    get_yearly_total_amount_info_using_source,
)

INCOMINGS = (btc.LoanPayment, btc.Income, btc.Debt)
OUTGOINGS = (btc.Withdrawal, btc.Loan, btc.Expense, btc.CreditCardPayment, btc.DebtPayment)

# the names the frontend sends -> the model to report on
MODELS_BY_NAME = {
    'expenses': btc.Expense,
    'deposits': btc.Deposit,
    'withdrawals': btc.Withdrawal,
    'incomes': btc.Income,
    'loans': btc.Loan,
    'loan_payment': btc.LoanPayment,
    'credit_card_payments': btc.CreditCardPayment,
    'debts': btc.Debt,
    'debt_payments': btc.DebtPayment,
    'bank_transfers': btc.BankTransfer,
}


def yearly_single_model(model_name, year=None):
    """{'months', '<table>': [12 totals], 'label'} or {} for a name that is not a known model."""
    model = MODELS_BY_NAME.get(model_name)
    if not model:
        return {}

    table = model.__tablename__
    return {
        'months': MONTHS,
        table: get_yearly_total_amount_info(CustomModel=model, year=year),
        'label': table.replace('_', ' ').title(),
    }


def yearly_all_models(year=None):
    return {'months': MONTHS, 'report': _yearly_by_table(btc.get_all(), year)}


def yearly_incomes_and_outgoings(year=None):
    return {
        'months': MONTHS,
        'incomings': _sum_by_month(INCOMINGS, year),
        'outgoings': _sum_by_month(OUTGOINGS, year),
    }


def monthly_incomings_and_outgoings():
    now = datetime.now()

    return {
        'incomings': _monthly_total(INCOMINGS, now.year, now.month),
        'outgoings': _monthly_total(OUTGOINGS, now.year, now.month),
    }


def bank_account_yearly_by_source(year=None):
    """Everything that moved through a bank account, each kind of record apart, plus the transfers."""
    report = {
        model.__tablename__: get_yearly_total_amount_info_using_source(CustomModel=model, year=year, source='bank')
        for model in btc.get_all() if model is not btc.BankTransfer
    }
    report[btc.BankTransfer.__tablename__] = get_yearly_total_amount_info(CustomModel=btc.BankTransfer, year=year)

    return {'months': MONTHS, 'report': report}


def credit_card_yearly_by_source(year=None):
    models = (btc.CreditCardPayment, btc.Expense, btc.Loan)
    return {'months': MONTHS, 'report': _yearly_by_table(models, year, source='card')}


def cash_yearly_by_source(year=None):
    models = (ctc.Loan, ctc.LoanPayment, ctc.Income, ctc.Expense, ctc.Debt, ctc.DebtPayment)
    return {'months': MONTHS, 'report': _yearly_by_table(models, year, source='cash')}


def cash_flow(year=None):
    """Incomes, expenses and what is left of each month."""
    expenses = get_yearly_total_amount_info(btc.Expense, year)
    incomes = get_yearly_total_amount_info(btc.Income, year)

    return {
        'months': MONTHS,
        'report': {
            'incomes': incomes,
            'expenses': expenses,
            'balances': [income - expense for income, expense in zip(incomes, expenses)],
        },
    }


# ------------------------------------------------------------------ helpers

def _yearly_by_table(models, year, source=None):
    if source:
        return {m.__tablename__: get_yearly_total_amount_info_using_source(CustomModel=m, year=year, source=source) for m in models}
    return {m.__tablename__: get_yearly_total_amount_info(CustomModel=m, year=year) for m in models}


def _sum_by_month(models, year):
    totals = [Decimal('0.00')] * 12
    for model in models:
        monthly = get_yearly_total_amount_info(CustomModel=model, year=year)
        totals = [total + month for total, month in zip(totals, monthly)]
    return totals


def _monthly_total(models, year, month):
    return sum((get_monthly_total_amount_info(CustomModel=m, year=year, month=month) for m in models), Decimal('0'))
