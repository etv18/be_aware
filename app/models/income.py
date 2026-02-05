from flask_babel import format_datetime

from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import event

from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes
from app.utils.date_handling import utcnow

class Income(db.Model):
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    is_cash = db.Column(db.Boolean, nullable=False, default=False)
    code = db.Column(db.String(50), nullable=False, server_default='TEMP')
    description = db.Column(db.String(255))

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    bank_account = relationship('BankAccount', back_populates='incomes')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, Income):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.INCOME, Income)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'is_cash': self.is_cash,
            'code': self.code,
            'description': self.description,
            'bank_account_id': self.bank_account_id,
            'bank_nick_name': self.bank_account.nick_name if self.bank_account else '-',
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
