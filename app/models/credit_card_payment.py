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
    bank_account = relationship('BankAccount', back_populates='credit_card_payments')

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'credit_card_id': self.credit_card_id,
            'bank_account_id': self.bank_account_id,
            'credit_card_nick_name': self.credit_card.nick_name if self.credit_card.nick_name else '-',
            'bank_account_nick_name': self.bank_account.nick_name if self.bank_account.nick_name else '-',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }