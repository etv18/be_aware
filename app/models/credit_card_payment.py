from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class CreditCardPayment(db.Model):
    __tablename__ = 'credit_card_payments'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'), nullable=False)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', name='bank_account_id'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    credit_card = relationship('CreditCard', back_populates='payments')