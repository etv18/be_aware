from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Expense(db.Model):

    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    is_cash = db.Column(db.Boolean, nullable=False, default=True)

    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    expense_category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    credit_card = relationship('CreditCard', back_populates='expenses')
    bank_account = relationship('BankAccount', back_populates='expenses')
    expense_category = relationship('ExpenseCategory', back_populates='expenses')

