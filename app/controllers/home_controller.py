"""What the home page and the forms need, each in one call."""
from datetime import datetime
from decimal import Decimal

from app.controllers import serializers as ser
from app.controllers._rest import data
from app.controllers.serializers import money
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.services import (
    bank_account_service, bank_service, credit_card_service, debt_service, expense_category_service,
    home_service, ledger_service, loan_service,
)
from app.utils.date_handling import get_years
from app.utils.filter_data import get_not_deleted_records


def dashboard():
    """The home page in one call."""
    accounts = get_not_deleted_records(model=BankAccount)
    cards = get_not_deleted_records(model=CreditCard)

    return data({
        **home_service.active_loans_and_debts(),
        'month': {name: money(value) for name, value in home_service.monthly_income_and_expense().items()},
        'year': datetime.now().year,
        'cash_balance': money(ledger_service.cash_balance()),
        'bank_total': money(sum((a.amount_available for a in accounts), Decimal())),
        'cards_used': money(sum((c.limit - c.amount_available for c in cards), Decimal())),
        'to_collect': money(loan_service.calculate_all_remainings()),
        'to_pay': money(debt_service.calculate_all_remainings()),
    })


def options():
    """Everything the forms need to fill their selects."""
    accounts = [a for a in bank_account_service.list_visible() if a.is_active]
    cards = [c for c in credit_card_service.list_visible() if c.is_active]

    return data({
        'banks': [ser.bank(b) for b in bank_service.list_banks()],
        'bank_accounts': [ser.bank_account(a) for a in accounts],
        'credit_cards': [ser.credit_card(c) for c in cards],
        'expense_categories': [ser.expense_category(c) for c in expense_category_service.list_visible()],
        'years': get_years(),
    })
