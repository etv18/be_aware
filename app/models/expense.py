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

    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),  # convert Decimal to float for JSON
            'is_cash': self.is_cash,
            'credit_card_id': self.credit_card_id,
            'bank_account_id': self.bank_account_id,
            'expense_category_id': self.expense_category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Related external properties of credit_card, bank_account and expense_category
            # they will be needed to be shown in the table on expenses/index template dinamically
            # with js.
            'credit_card_name': getattr(self.credit_card, 'nick_name', None),
            'bank_account_name': getattr(self.bank_account, 'nick_name', None),
            'expense_category_name': getattr(self.expense_category, 'name', None)
        }
