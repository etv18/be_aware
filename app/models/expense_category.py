from app.extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from decimal import Decimal

from app.utils.date_handling import utcnow

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    limit = db.Column(db.Numeric(10,2), server_default='0')
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    expenses = relationship('Expense', back_populates='expense_category', order_by='desc(Expense.created_at)')