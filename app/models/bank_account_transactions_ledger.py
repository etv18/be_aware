from app.extensions import db
from sqlalchemy.sql import func

import traceback
from decimal import Decimal

from app.utils import bank_transactional_classes
from app.utils.normalize_string import normalize_string
from app.utils.date_handling import utcnow

class BankAccountTransactionsLedger(db.Model):
    __tablename__ = 'bank_account_transactions_ledger'

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10,2), nullable=False)
    transaction_type = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(100), nullable=False)

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    before_update_balance = db.Column(db.Numeric(10,2), nullable=False)
    after_update_balance = db.Column(db.Numeric(10,2), nullable=False)

    is_increased = db.Column(db.Boolean, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )

    bank_account = db.relationship('BankAccount', back_populates='transaction_ledger')