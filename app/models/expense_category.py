from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from decimal import Decimal

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    limit = db.Column(db.Numeric(10,2), server_default='0')
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    expenses = relationship('Expense', back_populates='expense_category', order_by='desc(Expense.created_at)')