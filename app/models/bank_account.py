from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(120))
    amount_available = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    account_number = db.Column(db.Integer, nullable=True)

    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'))
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    bank = relationship('Bank', back_populates='bank_accounts')
    expenses = relationship('Expense', back_populates='bank_account', order_by='desc(Expense.created_at)')
    incomes = relationship('Income', back_populates='bank_account', order_by='desc(Income.created_at)')
    credit_card_payments = relationship('CreditCardPayment', back_populates='bank_account', order_by='desc(CreditCardPayment.created_at)')
    withdrawals = relationship('Withdrawal', back_populates='bank_account', order_by='desc(Withdrawal.created_at)')
    loans = relationship('Loan', back_populates='bank_account', order_by='desc(Loan.created_at)')
    loan_payments = relationship('LoanPayment', back_populates='bank_account', order_by='desc(LoanPayment.created_at)')
    debts = relationship('Debt', back_populates='bank_account', order_by='desc(Debt.created_at)')
    transaction_ledger = relationship('BankAccountTransactionsLedger', back_populates='bank_account')
    outgoing_transfers = relationship('BankTransfer', foreign_keys='BankTransfer.from_bank_account_id', back_populates='from_bank_account', order_by='desc(BankTransfer.created_at)')
    incoming_transfers = relationship('BankTransfer', foreign_keys='BankTransfer.to_bank_account_id', back_populates='to_bank_account', order_by='desc(BankTransfer.created_at)')