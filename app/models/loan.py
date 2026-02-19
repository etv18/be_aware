from flask_babel import format_datetime

from app.extensions import db
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from decimal import Decimal

from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes
from app.utils.date_handling import utcnow

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_cash = db.Column(db.Boolean)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'))
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    loan_payments = relationship('LoanPayment', back_populates='loan', order_by='desc(LoanPayment.created_at)', cascade='all, delete-orphan')
    bank_account = relationship('BankAccount', back_populates='loans')
    credit_card = relationship('CreditCard', back_populates='loans')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, Loan):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.LOAN, Loan)    

    def to_dict(self):
        return {
            'id': self.id,
            'person_name': self.person_name,
            'code': self.code,
            'amount': str(self.amount),
            'is_active': self.is_active,
            'f_is_active': 'ACTIVE' if self.is_active else 'PAID',
            'is_cash': self.is_cash,
            'f_is_cash': 'YES' if self.is_cash else 'NO',
            'bank_account_id': self.bank_account_id,
            'bank_account_nick_name': self.bank_account.nick_name if self.bank_account else '-',
            'credit_card_id': self.credit_card_id,
            'credit_card_nick_name': self.credit_card.nick_name if self.credit_card else '-',
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            'updated_at': self.updated_at.isoformat() if self.updated_at else '-',
            'raw_created_at': self.created_at.isoformat() if self.created_at else None,
            'description': self.description,
            'total_payments': str(self.total_payments()),
            'remaining_amount': str(self.remaining_amount())
        }


    def total_payments(self):
        db.session.refresh(self) 
        total = Decimal(0.0)
        for payment in self.loan_payments:
            total += payment.amount
        return total

    def remaining_amount(self):
        db.session.refresh(self) 
        remaining = self.amount - self.total_payments()
        if remaining < 0:
            return Decimal('0.00')
        return remaining.quantize(Decimal('0.00'))