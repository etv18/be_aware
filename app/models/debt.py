from flask_babel import format_datetime

from app.extensions import db
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from decimal import Decimal

from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes
from app.utils.date_handling import utcnow

class Debt(db.Model):
    __tablename__ = 'debts'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_cash = db.Column(db.Boolean)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

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

    debt_payments = relationship('DebtPayment', back_populates='debt', order_by='desc(DebtPayment.created_at)', cascade='all, delete-orphan')
    bank_account = relationship('BankAccount', back_populates='debts')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, Debt):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.DEBT, Debt)    

    def to_dict(self):
        return {
            'id': self.id,
            'person_name': self.person_name,
            'amount': str(self.amount),
            'is_active': self.is_active,
            'f_is_active': 'ACTIVE' if self.is_active else 'PAID',
            'is_cash': self.is_cash,
            'f_is_cash': 'YES' if self.is_cash else 'NO',
            'bank_account_id': self.bank_account_id,
            'bank_account_nick_name': self.bank_account.nick_name if self.bank_account else '-',
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            'updated_at': self.updated_at.isoformat() if self.updated_at else '-',
            'description': self.description,
            'total_payments': str(self.total_payments()),
            'remaining_amount': str(self.remaining_amount())
        }


    def total_payments(self):
        db.session.refresh(self) 
        total = Decimal(0.0)
        for payment in self.debt_payments:
            total += payment.amount
        return total

    def remaining_amount(self):
        db.session.refresh(self) 
        remaining = self.amount - self.total_payments()
        if remaining < 0:
            return Decimal('0.00')
        return remaining.quantize(Decimal('0.00'))