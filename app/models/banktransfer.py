from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class BankTransfer(db.Model):
    __tablename__ = 'bank_transfers'
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    from_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    to_bank_account_id =db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())   

    from_bank_account = relationship('BankAccount', foreign_keys=[from_bank_account_id], back_populates='outgoing_transfers')
    to_bank_account = relationship('BankAccount', foreign_keys=[to_bank_account_id], back_populates='incoming_transfers')
