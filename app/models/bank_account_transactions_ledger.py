from flask_babel import format_datetime
from app.extensions import db
from sqlalchemy.sql import func

import traceback
from decimal import Decimal

from app.utils import bank_transactional_classes as btc
from app.utils.normalize_string import normalize_string
from app.utils.date_handling import utcnow
from app.utils.cash_transactional_classes import is_a_cash_transaction


class BankAccountTransactionsLedger(db.Model):
    __tablename__ = 'bank_account_transactions_ledger'

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10,2), nullable=False)
    transaction_type = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(100), nullable=False)

    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
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

    bank_account = db.relationship('BankAccount', back_populates='transaction_ledger')

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'reference_code': self.reference_code,
            'bank_account_id': self.bank_account_id,
            'before_update_balance': self.before_update_balance,
            'after_update_balance': self.after_update_balance,
            'bank_account_nick_name': self.bank_account.nick_name,
            'created_at': format_datetime(self.created_at, 'EEE, dd MMM yyyy hh:mm a'),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def create(transaction):
        try:
            if isinstance(transaction, btc.BankTransfer):
                BankAccountTransactionsLedger._create_ledger_for_bank_transfer(transaction)
                return
            
            if not isinstance(transaction, btc.get_all()) or not transaction.bank_account: return

            amount = Decimal('0')
            before_update_balance = Decimal('0')
            after_update_balance = transaction.bank_account.amount_available
            
            increase_amount_available = (btc.LoanPayment, btc.Income, btc.Debt, btc.Deposit)
            reduce_amount_available = (btc.Withdrawal, btc.Loan, btc.Expense, btc.CreditCardPayment, btc.DebtPayment)
            
            if isinstance(transaction, increase_amount_available):
                amount = transaction.amount
                before_update_balance = transaction.bank_account.amount_available - transaction.amount #if the available amount increased to get the before update balance, it must be taken off the amount of the transaction. Eg: amount_available = 1, transaction.amount = 2, 1 + 2 = 3 -> 3 - 2 = 1 = before_update_amount 
            
            elif isinstance(transaction, reduce_amount_available):
                amount = -transaction.amount
                before_update_balance = transaction.bank_account.amount_available + transaction.amount

            ledger = BankAccountTransactionsLedger(
                amount=amount,
                transaction_type=normalize_string(transaction.__class__.__tablename__),
                reference_code=transaction.code,
                before_update_balance=before_update_balance,
                after_update_balance=after_update_balance,
                bank_account_id=transaction.bank_account_id
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
            if isinstance(transaction, btc.BankTransfer): return BankAccountTransactionsLedger._update_ledger_for_bank_transfer(transaction)
            
            if is_a_cash_transaction(transaction) or not transaction.bank_account_id: return BankAccountTransactionsLedger.delete(transaction)

            
            if not isinstance(transaction, btc.get_all()): return

            ledger = BankAccountTransactionsLedger.query.filter_by(reference_code = transaction.code).one_or_none()
            if not ledger: return BankAccountTransactionsLedger.create(transaction)

            amount = Decimal('0')
            before_update_balance = Decimal('0')
            after_update_balance = transaction.bank_account.amount_available
            
            increase_amount_available = (btc.LoanPayment, btc.Income, btc.Debt, btc.Deposit)
            reduce_amount_available = (btc.Withdrawal, btc.Loan, btc.Expense, btc.CreditCardPayment, btc.DebtPayment)
            
            if isinstance(transaction, increase_amount_available):
                amount = transaction.amount
                before_update_balance = transaction.bank_account.amount_available - transaction.amount #if the available amount increased to get the before update balance, it must be taken off the amount of the transaction. Eg: amount_available = 1, transaction.amount = 2, 1 + 2 = 3 -> 3 - 2 = 1 = before_update_amount 
            
            elif isinstance(transaction, reduce_amount_available):
                amount = -transaction.amount
                before_update_balance = transaction.bank_account.amount_available + transaction.amount

            ledger = BankAccountTransactionsLedger.query.filter_by(reference_code = transaction.code).first()

            ledger.amount = amount
            ledger.before_update_balance = before_update_balance
            ledger.after_update_balance = after_update_balance
            ledger.bank_account_id = transaction.bank_account_id
            
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e
        
    @staticmethod
    def delete(transaction):
        try:
            if isinstance(transaction, btc.BankTransfer): return BankAccountTransactionsLedger._delete_ledger_for_bank_transfer(transaction)

            if not isinstance(transaction, btc.get_all()): return
            
            ledger = BankAccountTransactionsLedger.query.filter_by(reference_code=transaction.code).first()

            if ledger:
                db.session.delete(ledger)
                db.session.commit()
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e  
        
    def _create_ledger_for_bank_transfer(transaction):
        try:
            origin_ledger = BankAccountTransactionsLedger(
                amount= -transaction.amount,
                transaction_type=f'OUTGOING {normalize_string(transaction.__class__.__tablename__)}',
                reference_code=transaction.code,
                before_update_balance= transaction.from_bank_account.amount_available + transaction.amount,
                after_update_balance=transaction.from_bank_account.amount_available,
                bank_account_id=transaction.from_bank_account_id
            )

            destination_ledger = BankAccountTransactionsLedger(
                amount= transaction.amount,
                transaction_type=f'INCOMING {normalize_string(transaction.__class__.__tablename__)}',
                reference_code=transaction.code,
                before_update_balance= transaction.to_bank_account.amount_available - transaction.amount,
                after_update_balance=transaction.to_bank_account.amount_available,
                bank_account_id=transaction.to_bank_account_id
            )
            db.session.add(origin_ledger)
            db.session.add(destination_ledger)
            db.session.commit()

        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e

    def _update_ledger_for_bank_transfer(transaction):
        try:
            transfer_ledgers = BankAccountTransactionsLedger.query.filter_by(reference_code = transaction.code).all()
            origin_ledger = None
            destination_ledger = None

            for ledger in transfer_ledgers:
                if ledger.amount >= 0:
                    destination_ledger = ledger
                else:
                    origin_ledger = ledger

            
            origin_ledger.amount = -transaction.amount
            origin_ledger.before_update_balance = transaction.from_bank_account.amount_available + transaction.amount
            origin_ledger.after_update_balance = transaction.from_bank_account.amount_available

            destination_ledger.amount = transaction.amount
            destination_ledger.before_update_balance = transaction.to_bank_account.amount_available - transaction.amount
            destination_ledger.after_update_balance = transaction.to_bank_account.amount_available
            destination_ledger.bank_account_id = transaction.to_bank_account_id

            db.session.commit()

        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e

    def _delete_ledger_for_bank_transfer(transaction):
        try:
            BankAccountTransactionsLedger.query.filter_by(
                reference_code=transaction.code
            ).delete()

            db.session.commit()

        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            raise e 
