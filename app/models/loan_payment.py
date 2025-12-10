from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import event

from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes

class LoanPayment(db.Model):
    __tablename__ = 'loan_payment'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    is_cash = db.Column(db.Boolean, nullable=False)
    
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', name='bank_account_id'))
    code = db.Column(db.String(50), nullable=False, server_default='TEMP')

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())  

    loan = relationship('Loan', back_populates='loan_payments')
    bank_account = relationship('BankAccount', back_populates='loan_payments')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, LoanPayment):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.LOAN_PAYMENT, LoanPayment)