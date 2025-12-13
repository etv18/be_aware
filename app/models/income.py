from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import event

from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes

class Income(db.Model):
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    is_cash = db.Column(db.Boolean, nullable=False, default=False)
    code = db.Column(db.String(50), nullable=False, server_default='TEMP')
    description = db.Column(db.String(255))

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    bank_account = relationship('BankAccount', back_populates='incomes')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, Income):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.INCOME, Income)