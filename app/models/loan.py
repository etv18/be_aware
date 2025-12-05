from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from decimal import Decimal

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_cash = db.Column(db.Boolean)

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    description = db.Column(db.String(200))

    loan_payments = relationship('LoanPayment', back_populates='loan')
    bank_account = relationship('BankAccount', back_populates='loans')

    def total_payments(self):
        db.session.refresh(self) 
        total = Decimal(0.0)
        for payment in self.loan_payments:
            total += payment.amount
        return total

    def remaining_amount(self):
        db.session.refresh(self) 
        remaining = self.amount - self.total_payments()
        if remaining < 0:
            return Decimal("0.00")
        return remaining.quantize(Decimal("0.00"))