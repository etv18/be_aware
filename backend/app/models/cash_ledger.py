from flask_babel import format_datetime

from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from decimal import Decimal

from app.utils import cash_transactional_classes as ctc
from app.utils.normalize_string import normalize_string
from app.utils.date_handling import utcnow
from app.utils.transactions import save

class CashLedger(db.Model):
    __tablename__ = 'cash_ledger' 

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10,2), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(100), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        onupdate=utcnow, #internally sqlalchemy will exectute the function so dont add the parentheses otherwise it'll break down when creating the record in the db
    )

    def to_dict(self):
        return {
            "id": self.id,
            "amount": float(self.amount) if isinstance(self.amount, Decimal) else self.amount,
            "type": self.type,
            "reference_code": self.reference_code,
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            'raw_created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def create(transaction, commit=True):
        try:
            
            if not isinstance(transaction, ctc.get_all()): return
                        
            '''
            this if statement checks if a transaction can be arithmetically operated with CashLedger model, in 
            other words make sure only objects from Withdrawal or Models which have an is_cash=True property can
            be saved into cash_ledger table in the database
            '''
            
            amount = Decimal('0')
            if isinstance(transaction, (ctc.Withdrawal, ctc.LoanPayment, ctc.Income, ctc.Debt)):
                
                amount = transaction.amount
            if isinstance(transaction, (ctc.Expense, ctc.Loan, ctc.DebtPayment, ctc.Deposit)):
                amount = -transaction.amount
                

            ledger = CashLedger(
                amount=amount,
                type=normalize_string(transaction.__class__.__tablename__),
                reference_code=transaction.code
            )
            
            db.session.add(ledger)
            save(commit)
            
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def update(transaction, commit=True):
        try:
            if not isinstance(transaction, ctc.get_all()):
                return
            
            amount = transaction.amount
            if isinstance(transaction, (ctc.Expense, ctc.Loan, ctc.DebtPayment, ctc.Deposit)):
                amount = -amount #If a transaction is instance of Expense or Loan the amount must be negative

            ledger = CashLedger.query.filter_by(reference_code=transaction.code).first()
            if ledger:
                ledger.amount = amount
                save(commit)
            else:
                CashLedger.create(transaction, commit=commit)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete(transaction, commit=True):
        try:
            if not isinstance(transaction, ctc.get_all()):
                return
            
            ledger = CashLedger.query.filter_by(reference_code=transaction.code).first()

            if ledger:
                db.session.delete(ledger)
                save(commit)
        except Exception as e:
            db.session.rollback()
            raise e  

    @staticmethod
    def update_or_delete(transaction, delete_ledger=False, commit=True):
        try:
            if not isinstance(transaction, ctc.get_all()):
                return
            
            if delete_ledger:
                CashLedger.delete(transaction, commit=commit)
                return
            
            if isinstance(transaction, (ctc.Withdrawal, ctc.Deposit)): # is instance of Withdrawal
                CashLedger.update(transaction, commit=commit)
                return
            
            if transaction.is_cash:
                CashLedger.update(transaction, commit=commit)
            else:
                CashLedger.delete(transaction, commit=commit)

        except Exception as e:
            db.session.rollback()
            raise e
