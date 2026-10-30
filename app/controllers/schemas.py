"""What the controllers accept in a JSON body. A request that does not fit answers 422 with the offending fields.

The field names are the keyword arguments of the services, so a body goes straight into a service call.
`created_at` is always optional (it defaults to now) and is local wall-clock time.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Body(BaseModel):
    model_config = ConfigDict(extra='ignore', str_strip_whitespace=True)


class Dated(Body):
    created_at: Optional[datetime] = None


# ------------------------------------------------------------------ money in and out

class ExpenseIn(Dated):
    amount: Decimal
    is_cash: bool
    expense_category_id: int
    description: str = Field(min_length=1, max_length=150)
    credit_card_id: Optional[int] = None
    bank_account_id: Optional[int] = None


class IncomeIn(Dated):
    amount: Decimal
    is_cash: bool
    bank_account_id: Optional[int] = None
    description: Optional[str] = Field(default=None, max_length=255)


class WithdrawalIn(Dated):
    amount: Decimal
    bank_account_id: int
    description: Optional[str] = Field(default=None, max_length=255)


DepositIn = WithdrawalIn


class BankTransferCreate(Dated):
    amount: Decimal
    from_bank_account_id: int
    to_bank_account_id: int


class BankTransferUpdate(Dated):
    amount: Decimal
    to_bank_account_id: int


class CreditCardPaymentCreate(Dated):
    credit_card_id: int
    amount: Decimal
    is_cashback: bool = False
    bank_account_id: Optional[int] = None


class CreditCardPaymentUpdate(Dated):
    amount: Decimal
    is_cashback: bool = False
    bank_account_id: Optional[int] = None


# ------------------------------------------------------------------ loans and debts

class LoanIn(Dated):
    amount: Decimal
    is_cash: bool
    person_name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=200)
    bank_account_id: Optional[int] = None
    credit_card_id: Optional[int] = None


class LoanUpdate(LoanIn):
    is_active: bool = True


class DebtIn(Dated):
    amount: Decimal
    is_cash: bool
    person_name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=200)
    bank_account_id: Optional[int] = None


class DebtUpdate(DebtIn):
    is_active: bool = True


class LoanPaymentCreate(Dated):
    loan_id: int
    amount: Decimal
    is_cash: bool
    bank_account_id: Optional[int] = None


class LoanPaymentUpdate(Dated):
    amount: Decimal
    is_cash: bool
    bank_account_id: Optional[int] = None


class DebtPaymentCreate(Dated):
    debt_id: int
    amount: Decimal
    is_cash: bool
    bank_account_id: Optional[int] = None


class DebtPaymentUpdate(LoanPaymentUpdate):
    pass


# ------------------------------------------------------------------ products and reference data

class BankIn(Body):
    name: str = Field(min_length=1, max_length=100)


class BankAccountIn(Body):
    nick_name: str = Field(min_length=1, max_length=120)
    account_number: Optional[str] = Field(default=None, max_length=6)
    amount_available: Decimal
    bank_id: int


class CreditCardIn(Body):
    nick_name: str = Field(min_length=1, max_length=100)
    limit: Decimal
    amount_available: Decimal
    bank_id: int


class ExpenseCategoryIn(Body):
    name: str = Field(max_length=100)
    limit: Decimal = Decimal('0')


class CashAdjustmentIn(Dated):
    amount: Decimal


class LoginIn(Body):
    username: str
    password: str
