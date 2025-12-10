from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Withdrawal(db.Model):
    __tablename__ = 'withdrawals'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    description = db.Column(db.String(255))
    code = db.Column(db.String(50), nullable=False)
    
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    bank_account = relationship('BankAccount', back_populates='withdrawals')