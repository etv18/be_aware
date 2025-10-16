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
    expenses = relationship('Expense', back_populates='bank_account')
    incomes = relationship('Income', back_populates='bank_account')