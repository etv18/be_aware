from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import traceback
from decimal import Decimal

from app.utils import transactional_classes

class CashLedger(db.Model):
    __tablename__ = 'cash_ledger' 

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10,2), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "amount": float(self.amount) if isinstance(self.amount, Decimal) else self.amount,
            "type": self.type,
            "reference_code": self.reference_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def create(transaction):
        try:
            if not isinstance(transaction, transactional_classes.get_all()):
                return
            
            '''
            this if statement checks if a transaction can be arithmetically operated with CashLedger model, in 
            other words make sure only objects from Withdrawal or Models which have an is_cash=True property can
            be saved into cash_ledger table in the database
            '''
            if isinstance(transaction, transactional_classes.Withdrawal) or transaction.is_cash:
                amount = transaction.amount
                if isinstance(transaction, (transactional_classes.Expense, transactional_classes.Loan)):
                    amount = -amount
                
                ledger = CashLedger(
                    amount=amount,
                    type=transaction.__class__.__tablename__,
                    reference_code=transaction.code
                )

                db.session.add(ledger)
                db.session.commit()
        except Exception as e:
            print('Error on cash ledger file: ', e)
            traceback.print_exc()
            db.session.rollback()
            raise e
        
    @staticmethod
    def update(transaction):
        try:
            if not isinstance(transaction, transactional_classes.get_all()):
                return
            
            amount = transaction.amount
            if isinstance(transaction, (transactional_classes.Expense, transactional_classes.Loan)):
                amount = -amount #If a transaction is instance of Expense or Loan the amount must be negative

            ledger = CashLedger.query.filter_by(reference_code=transaction.code).first()
            if ledger:
                ledger.amount = amount
                db.session.commit()
            else:
                CashLedger.create(transaction)
        except Exception as e:
            print('Error on cash ledger file: ', e)
            traceback.print_exc()
            db.session.rollback()
            raise e

    @staticmethod
    def delete(transaction):
        try:
            if not isinstance(transaction, transactional_classes.get_all()):
                return
            
            ledger = CashLedger.query.filter_by(reference_code=transaction.code).first()

            if ledger:
                db.session.delete(ledger)
                db.session.commit()
        except Exception as e:
            print('Error on cash ledger file: ', e)
            traceback.print_exc()
            db.session.rollback()
            raise e  

    @staticmethod
    def update_or_delete(transaction, delete_ledger=False):
        try:
            if not isinstance(transaction, transactional_classes.get_all()):
                return
            
            if delete_ledger:
                CashLedger.delete(transaction)
                return
            
            if isinstance(transaction, transactional_classes.Withdrawal): # is instance of Withdrawal
                CashLedger.update(transaction)
                return
            
            if transaction.is_cash:
                CashLedger.update(transaction)
            else:
                CashLedger.delete(transaction)

        except Exception as e:
            print('Error on cash ledger file: ', e)
            traceback.print_exc()
            db.session.rollback()
            raise e
