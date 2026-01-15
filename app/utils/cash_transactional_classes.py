from app.models.expense import Expense
from app.models.income import Income
from app.models.loan_payment import LoanPayment
from app.models.loan import Loan
from app.models.withdrawal import Withdrawal
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment

def get_all():
    return (
        Withdrawal,
        Loan,
        LoanPayment,
        Income,
        Expense,
        Debt,
        DebtPayment,
    )

def is_a_cash_transaction(transaction):
    is_cash = getattr(transaction, 'is_cash', False)
    if is_cash: 
        return transaction.is_cash
    return False