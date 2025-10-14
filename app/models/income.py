from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Income(db.Model):
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    is_cash = db.Column(db.Boolean, nullable=False, default=False)

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    bank_account = relationship('BankAccount', back_populates='incomes')
