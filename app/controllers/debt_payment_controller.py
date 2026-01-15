from flask import request, jsonify

from decimal import Decimal

from app.extensions import db
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.debt_payment import DebtPayment
from app.models.debt import Debt
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import is_decimal_type
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, BankAccountDoesNotExists

def create():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        bank_account_id = None
        debt_id = int(request.form['debt-id'])

        debt = Debt.query.get(debt_id)
        if not debt:
            return jsonify({'error': 'Debt record was not found'}), 400

        if debt.total_payments() >= debt.amount:
            return jsonify({
                'message': 'Debt is already fully paid',
                'is_paid': True
            }), 200
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if not is_cash:
            bank_account_id = int(request.form.get('select-bank-account'))
            _subtract_money_from_back_account(bank_account_id, amount)
        debt_payment = DebtPayment(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id,
            debt_id=debt_id
        )
        db.session.add(debt_payment)
        db.session.commit()

        _update_debt_is_active(debt)
        
        #CashLedger.create(debt_payment)
        #if debt_payment.bank_account_id: BankAccountTransactionsLedger.create(debt_payment)

        return jsonify({'message': 'Debt payment created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        raise e

def _update_debt_is_active(debt):
    db.session.refresh(debt)  # <-- refresh from DB
    debt.is_active = debt.remaining_amount() > 0
    db.session.commit()

def _add_money_to_back_account(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    
    bank_account.amount_available += amount

def _subtract_money_from_back_account(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    
    bank_account.amount_available -= amount