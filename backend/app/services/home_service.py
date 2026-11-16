"""Figures for the home page: expenses against incomes. Read only."""
from datetime import datetime

from app.models.expense import Expense
from app.models.income import Income
from app.services import debt_service, loan_service
from app.utils.date_handling import MONTHS
from app.utils.filter_data import get_monthly_total_amount_info, get_yearly_total_amount_info


def active_loans_and_debts():
    return {
        'active_loans': loan_service.count_by_status()['actives'],
        'active_debts': debt_service.count_by_status()['actives'],
    }


def monthly_income_and_expense():
    """Totals of the current month."""
    now = datetime.now()

    return {
        'incomes': get_monthly_total_amount_info(Income, now.year, now.month),
        'expenses': get_monthly_total_amount_info(Expense, now.year, now.month),
    }


def yearly_income_and_expense():
    """Totals of each month of the current year."""
    year = datetime.now().year

    return {
        'months': MONTHS,
        'expenses': get_yearly_total_amount_info(Expense, year),
        'incomes': get_yearly_total_amount_info(Income, year),
    }
