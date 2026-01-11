from app.extensions import db
from sqlalchemy.sql import func

import traceback
from decimal import Decimal

from app.utils import bank_transactional_classes as btc
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

    @staticmethod
    def create(transaction):
        try:
            if not isinstance(transaction, btc.get_all()) or not transaction.bank_account: return

            amount = Decimal('0')
            before_update_balance = Decimal('0')
            after_update_balance = transaction.bank_account.amount_available
            
            increase_amount_available = (btc.LoanPayment, btc.Income)
            reduce_amount_available = (btc.Withdrawal, btc.Loan, btc.Expense, btc.CreditCardPayment)
            
            if isinstance(transaction, increase_amount_available):
                amount = transaction.amount
                before_update_balance = transaction.bank_account.amount_available - transaction.amount #if the available amount increased to get the before update balance, it must be taken off the amount of the transaction. Eg: amount_available = 1, transaction.amount = 2, 1 + 2 = 3 -> 3 - 2 = 1 = before_update_amount 
            
            elif isinstance(transaction, reduce_amount_available):
                amount = -transaction.amount
                before_update_balance = transaction.bank_account.amount_available + transaction.amount

            elif isinstance(transaction, btc.BankTransfer):
                pass

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
            print('Error on cash ledger file: ', e)
            traceback.print_exc()
            db.session.rollback()
            raise e
        
'''
        *** ADD ***
            LoanPayment,
            Income,
        
        *** MINUS ***
            Withdrawal,
            Loan,
            Expense,
            CreditCardPayment,

        *** BOTH ***
            BankTransfer,

'''