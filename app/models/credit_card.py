from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.utils.date_handling import utcnow

class CreditCard(db.Model):
    __tablename__ = 'credit_cards'

    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(100))
    amount_available = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    limit = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    #Setting up foreign key from banks table
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    #This allows sqlalchemy to navigated between relationships in python code
    bank = relationship('Bank', back_populates='credit_cards')
    expenses = relationship('Expense', back_populates='credit_card', order_by='desc(Expense.created_at)')
    payments = relationship('CreditCardPayment', back_populates='credit_card', order_by='desc(CreditCardPayment.created_at)') 
    transaction_ledger = relationship('CreditCardTransactionsLedger', back_populates='credit_card', order_by='desc(CreditCardTransactionsLedger.created_at)', cascade='all, delete-orphan')  