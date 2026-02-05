from flask_babel import format_datetime

from app.extensions import db
from sqlalchemy.sql import func

import traceback
from decimal import Decimal

from app.models.credit_card_payment import CreditCardPayment
from app.models.expense import Expense
from app.utils.normalize_string import normalize_string
from app.utils.date_handling import utcnow
from app.utils.cash_transactional_classes import is_a_cash_transaction


class CreditCardTransactionsLedger(db.Model):
    __tablename__ = 'credit_card_transactions_ledger'

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10,2), nullable=False)
    transaction_type = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(100), nullable=False)

    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'), nullable=False)
    before_update_balance = db.Column(db.Numeric(10,2), nullable=False)
    after_update_balance = db.Column(db.Numeric(10,2), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    credit_card = db.relationship('CreditCard', back_populates='transaction_ledger')

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'reference_code': self.reference_code,
            'credit_card_id': self.credit_card_id,
            'before_update_balance': self.before_update_balance,
            'after_update_balance': self.after_update_balance,
            'credit_card_nick_name': self.credit_card.nick_name,
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def create(transaction):
        try:
            
            if not isinstance(transaction, (Expense, CreditCardPayment)) or not transaction.credit_card_id: return

            amount = Decimal('0')
            before_update_balance = Decimal('0')
            after_update_balance = transaction.credit_card.amount_available
            
            if isinstance(transaction, CreditCardPayment):
                amount = transaction.amount
                before_update_balance = transaction.credit_card.amount_available - transaction.amount #if the available amount increased to get the before update balance, it must be taken off the amount of the transaction. Eg: amount_available = 1, transaction.amount = 2, 1 + 2 = 3 -> 3 - 2 = 1 = before_update_amount 
            
            elif isinstance(transaction, Expense):
                amount = -transaction.amount
                before_update_balance = transaction.credit_card.amount_available + transaction.amount

            ledger = CreditCardTransactionsLedger(
                amount=amount,
                transaction_type=normalize_string(transaction.__class__.__tablename__),
                reference_code=transaction.code,
                before_update_balance=before_update_balance,
                after_update_balance=after_update_balance,
                credit_card_id=transaction.credit_card_id
            )

            db.session.add(ledger)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            db.session.rollback() 
            raise e 

    @staticmethod
    def update(transaction):
        try:            
            if is_a_cash_transaction(transaction) or not transaction.credit_card_id: return CreditCardTransactionsLedger.delete(transaction)

            
            if not isinstance(transaction, (Expense, CreditCardPayment)) or not transaction.credit_card_id: return

            ledger = CreditCardTransactionsLedger.query.filter_by(reference_code = transaction.code).one_or_none()
            if not ledger: return CreditCardTransactionsLedger.create(transaction)

            amount = Decimal('0')
            before_update_balance = Decimal('0')
            after_update_balance = transaction.credit_card.amount_available
        
            
            if isinstance(transaction, CreditCardPayment):
                amount = transaction.amount
                before_update_balance = transaction.credit_card.amount_available - transaction.amount #if the available amount increased to get the before update balance, it must be taken off the amount of the transaction. Eg: amount_available = 1, transaction.amount = 2, 1 + 2 = 3 -> 3 - 2 = 1 = before_update_amount 
            
            elif isinstance(transaction, Expense):
                amount = -transaction.amount
                before_update_balance = transaction.credit_card.amount_available + transaction.amount

            ledger = CreditCardTransactionsLedger.query.filter_by(reference_code = transaction.code).first()

            ledger.amount = amount
            ledger.before_update_balance = before_update_balance
            ledger.after_update_balance = after_update_balance
            ledger.credit_card_id = transaction.credit_card_id
            
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e
        
    @staticmethod
    def delete(transaction):
        try:

            if not isinstance(transaction, (Expense, CreditCardPayment)) and not transaction.credit_card_id: return
            
            ledger = CreditCardTransactionsLedger.query.filter_by(reference_code=transaction.code).first()

            if ledger:
                db.session.delete(ledger)
                db.session.commit()
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e  