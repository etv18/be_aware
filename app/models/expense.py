from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.extensions import db
from app.utils.code_generator import generate_montly_sequence
from app.utils import prefixes
from app.utils.date_handling import utcnow

class Expense(db.Model):

    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    is_cash = db.Column(db.Boolean, nullable=False)

    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    expense_category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    credit_card = relationship('CreditCard', back_populates='expenses')
    bank_account = relationship('BankAccount', back_populates='expenses')
    expense_category = relationship('ExpenseCategory', back_populates='expenses')

    @event.listens_for(db.session, 'before_flush')
    def assign_code(session, flush_context, instances=None):
        for obj in session.new:
            if isinstance(obj, Expense):
                if not obj.code:
                    obj.code = generate_montly_sequence(prefixes.EXPENSE, Expense)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': str(self.amount),
            'is_cash': self.is_cash,
            'credit_card_id': self.credit_card_id,
            'bank_account_id': self.bank_account_id,
            'expense_category_id': self.expense_category_id,
            'description': self.description,  
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            
            # Related external properties of credit_card, bank_account and expense_category
            # they will be needed to be shown in the table on expenses/index template dinamically
            # with js.
            'credit_card_name': getattr(self.credit_card, 'nick_name', None),
            'bank_account_name': getattr(self.bank_account, 'nick_name', None),
            'expense_category_name': self.expense_category.name.lower().title() if self.expense_category else None
        }
