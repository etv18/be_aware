from flask_babel import format_datetime

from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.extensions import db
from app.utils import prefixes
from app.utils.code_generator import generate_montly_sequence
from app.utils.date_handling import utcnow

class BankTransfer(db.Model):
    __tablename__ = 'bank_transfers'
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    from_bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    to_bank_account_id =db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    ) 

    from_bank_account = relationship('BankAccount', foreign_keys=[from_bank_account_id], back_populates='outgoing_transfers')
    to_bank_account = relationship('BankAccount', foreign_keys=[to_bank_account_id], back_populates='incoming_transfers')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, BankTransfer):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.BANK_TRANSFER, BankTransfer)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'amount': self.amount,
            'from_bank_account_id': self.from_bank_account_id,
            'to_bank_account_id': self.to_bank_account_id,
            'from_bank_account_nick_name': self.from_bank_account.nick_name if self.from_bank_account else None,
            'to_bank_account_nick_name': self.to_bank_account.nick_name if self.to_bank_account else None,
            'code': self.code,
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'raw_created_at': self.created_at.isoformat() if self.created_at else None,
        }