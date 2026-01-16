from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.extensions import db
from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes

class Deposit(db.Model):
    __tablename__ = 'deposits'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    description = db.Column(db.String(255))
    code = db.Column(db.String(50), nullable=False)
    
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    bank_account = relationship('BankAccount', back_populates='deposits')
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount) if self.amount is not None else 0.0,
            'description': self.description,
            'code': self.code,
            'bank_account_id': self.bank_account_id,
            'bank_account_nick_name': self.bank_account.nick_name if self.bank_account else '-',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, Deposit):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.DEPOSIT, Deposit)