from app.models.expense import Expense
from app.models.income import Income
from app.models.loan_payment import LoanPayment
from app.models.loan import Loan
from app.models.withdrawal import Withdrawal
from app.models.credit_card_payment import CreditCardPayment
from app.models.banktransfer import BankTransfer

def get_all():
    return (
        Withdrawal,
        Loan,
        LoanPayment,
        Income,
        Expense,
        CreditCardPayment,
        BankTransfer,
    )