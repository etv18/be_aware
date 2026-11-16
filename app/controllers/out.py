"""What each JSON response contains: one Pydantic model per kind of record.

These models are the single description of the API's output:
  * `Resource.present()` (controllers/_rest.py) runs every record through its model before it is sent, so a
    serializer that returns the wrong shape fails loudly instead of silently changing the API.
  * app/openapi.py turns them into the OpenAPI document, and the frontend generates its TypeScript types from that.

Conventions (the same ones serializers.py follows):
  * money is a string with two decimals ("1234.50"), never a number
  * `created_at` / `updated_at` are local wall-clock ISO text without an offset ("2026-10-30T12:00:00")
  * a related record contributes its id and its readable name (`bank_account_id`, `bank_account_name`)
  * every field is always present; "nothing" is null
"""
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Money = str


class Out(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Stamped(Out):
    created_at: Optional[str] = Field(description='Local wall-clock time, ISO text without an offset.')
    updated_at: Optional[str]


# ------------------------------------------------------------------ money in and out

class ExpenseOut(Stamped):
    id: int
    code: Optional[str]
    amount: Money
    is_cash: bool
    description: Optional[str]
    expense_category_id: Optional[int]
    expense_category_name: Optional[str]
    credit_card_id: Optional[int]
    credit_card_name: Optional[str]
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]


class IncomeOut(Stamped):
    id: int
    code: Optional[str]
    amount: Money
    is_cash: bool
    description: Optional[str]
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]


class CashMovementOut(Stamped):
    """A withdrawal or a deposit: money between cash and one bank account."""
    id: int
    code: Optional[str]
    amount: Money
    description: Optional[str]
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]


class BankTransferOut(Stamped):
    id: int
    code: Optional[str]
    amount: Money
    from_bank_account_id: Optional[int]
    from_bank_account_name: Optional[str]
    to_bank_account_id: Optional[int]
    to_bank_account_name: Optional[str]


class CreditCardPaymentOut(Stamped):
    id: int
    code: Optional[str]
    amount: Money
    is_cashback: bool
    credit_card_id: Optional[int]
    credit_card_name: Optional[str]
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]


# ------------------------------------------------------------------ loans and debts

class ObligationOut(Stamped):
    id: int
    code: Optional[str]
    person_name: str
    amount: Money
    is_cash: bool
    is_active: bool
    status: Literal['active', 'paid']
    description: Optional[str]
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]
    total_paid: Money
    remaining_amount: Money


class DebtOut(ObligationOut):
    pass


class LoanOut(ObligationOut):
    credit_card_id: Optional[int]
    credit_card_name: Optional[str]


class PaymentOut(Stamped):
    id: int
    code: Optional[str]
    amount: Money
    is_cash: bool
    person_name: Optional[str]
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]


class LoanPaymentOut(PaymentOut):
    loan_id: int


class DebtPaymentOut(PaymentOut):
    debt_id: int


# ------------------------------------------------------------------ products and reference data

class BankOut(Stamped):
    id: int
    name: str


class BankAccountOut(Stamped):
    id: int
    nick_name: str
    account_number: Optional[str]
    amount_available: Money
    is_active: bool
    bank_id: Optional[int]
    bank_name: Optional[str]


class CreditCardOut(Stamped):
    id: int
    nick_name: str
    limit: Money
    amount_available: Money
    used: Money
    is_active: bool
    bank_id: Optional[int]
    bank_name: Optional[str]


class ExpenseCategoryOut(Stamped):
    id: int
    name: str
    display_name: str
    limit: Optional[Money]


# ------------------------------------------------------------------ ledgers

class CashLedgerOut(Stamped):
    id: int
    reference_code: Optional[str]
    type: Optional[str]
    amount: Money
    is_adjustment: bool


class _ProductLedgerOut(Stamped):
    id: int
    reference_code: Optional[str]
    transaction_type: Optional[str]
    amount: Money
    before_balance: Optional[Money]
    after_balance: Optional[Money]


class BankLedgerOut(_ProductLedgerOut):
    bank_account_id: Optional[int]
    bank_account_name: Optional[str]


class CardLedgerOut(_ProductLedgerOut):
    credit_card_id: Optional[int]
    credit_card_name: Optional[str]


# ------------------------------------------------------------------ meta of the lists

class ListMeta(BaseModel):
    """`meta` of a list response. Some resources add figures of their own (they are allowed, not all are typed)."""
    model_config = ConfigDict(extra='allow')

    count: int
    total: Optional[Money] = Field(default=None, description='Sum of the amounts, for resources that have an amount.')


class Budget(Out):
    limit: Money
    spent: Money
    left: Money


class ExpenseListMeta(ListMeta):
    budget: Budget


# ------------------------------------------------------------------ other answers

class OptionsOut(Out):
    """Everything the forms need to fill their selects."""
    banks: list[BankOut]
    bank_accounts: list[BankAccountOut]
    credit_cards: list[CreditCardOut]
    expense_categories: list[ExpenseCategoryOut]
    years: list[int]


class MonthTotals(Out):
    incomes: Money
    expenses: Money


class DashboardOut(Out):
    active_loans: int
    active_debts: int
    month: MonthTotals
    year: int
    cash_balance: Money
    bank_total: Money
    cards_used: Money
    to_collect: Money
    to_pay: Money


class UserOut(Out):
    id: int
    username: str


class SessionOut(Out):
    authenticated: bool
    user: Optional[UserOut]
    csrf_token: str = Field(description='Send it back in an X-CSRFToken header on POST, PUT and DELETE.')
    env_name: Literal['development', 'testing', 'production']
    env_label: str = Field(description='DEV, TEST or PROD: the badge of the navbar.')


class YearlyReportOut(BaseModel):
    """One kind of record per month. Besides `months` and `label` there is one list of 12 totals named after the table."""
    model_config = ConfigDict(extra='allow')

    months: list[str]
    label: str


# ------------------------------------------------------------------ which model describes which serializer

def _by_serializer():
    from app.controllers import serializers as ser

    return {
        ser.expense: ExpenseOut,
        ser.income: IncomeOut,
        ser.withdrawal: CashMovementOut,   # deposit is the same function
        ser.banktransfer: BankTransferOut,
        ser.credit_card_payment: CreditCardPaymentOut,
        ser.loan: LoanOut,
        ser.debt: DebtOut,
        ser.loan_payment: LoanPaymentOut,
        ser.debt_payment: DebtPaymentOut,
        ser.bank: BankOut,
        ser.bank_account: BankAccountOut,
        ser.credit_card: CreditCardOut,
        ser.expense_category: ExpenseCategoryOut,
        ser.cash_ledger: CashLedgerOut,
        ser.bank_ledger: BankLedgerOut,
        ser.card_ledger: CardLedgerOut,
    }


def out_for(serialize):
    """The model of a serializer function (None for one that is not described yet)."""
    return _by_serializer().get(serialize)


META_FOR = {ExpenseOut: ExpenseListMeta}
