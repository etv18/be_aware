from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class LoanPayment(db.Model):
    __tablename__ = 'loan_payment'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', name='bank_account_id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())  

    loan = relationship('Loan', back_populates='loan_payments')
    bank_account = relationship('BankAccount', back_populates='loan_payments')

