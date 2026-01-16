from flask import request, jsonify

from decimal import Decimal
import traceback

from app.extensions import db
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.debt_payment import DebtPayment
from app.models.debt import Debt
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import is_decimal_type
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, BankAccountDoesNotExists, NoAvailableMoney, AmountGreaterThanAvailableMoney

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
            bank_account_id = request.form.get('select-bank-account')
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
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def update(id):
    try:
        debt_payment = DebtPayment.query.get(id)
        if not debt_payment:
            return jsonify({'error': 'Debt payment record was not found'}), 400

        new_amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')

        if(new_amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        new_bank_account_id = None
        is_cash = request.form.get('is-cash') == 'on'
        selected_bank_account = request.form.get('select-bank-account')
        debt_id = int(request.form['debt-id'])  

        bank_account = BankAccount.query.get(selected_bank_account)
        if not is_cash and not bank_account: raise BankAccountDoesNotExists('Please select a bank account')
        new_bank_account_id = selected_bank_account

        if not is_cash:
            _update_bank_account_money_on_update(
                old_ba_id=debt_payment.bank_account_id, 
                new_ba_id=new_bank_account_id, 
                old_amount=debt_payment.amount, 
                new_amount=new_amount
            )
        elif debt_payment.bank_account:
            debt_payment.bank_account.amount_available += debt_payment.amount

        debt = Debt.query.get(debt_id)
        if not debt:
            return jsonify({'error': 'Debt record was not found'}), 400
        
        debt_payment.amount = new_amount
        debt_payment.is_cash = is_cash
        debt_payment.bank_account_id = new_bank_account_id

        db.session.commit()

        #CashLedger.update_or_delete(debt_payment)
        #BankAccountTransactionsLedger.update(debt_payment)

        _update_debt_is_active(debt)

        return jsonify({'message': 'Debt payment updated successfully'}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

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
    
    if amount > bank_account.amount_available:
        raise AmountGreaterThanAvailableMoney(f"Insufficient founds from '{bank_account.nick_name}' bank account.")
    
    bank_account.amount_available -= amount

def _update_bank_account_money_on_update(old_ba_id, new_ba_id, old_amount, new_amount):
    if (old_ba_id == new_ba_id) and (old_amount == new_amount): return

    old_bank_account = None
    new_bank_account = None

    try:
        if old_ba_id: #if the bank account id is true it means it's bank account to bank account transaction
            old_bank_account = BankAccount.query.get(old_ba_id)
            if not old_bank_account:
                raise BankAccountDoesNotExists('Bank account does not exists.')   
            old_bank_account.amount_available += old_amount; #refund the money used to the previous bank account
        
        new_bank_account = BankAccount.query.get(new_ba_id)

        if not new_bank_account:
            raise BankAccountDoesNotExists('Bank account does not exists.')

        if new_bank_account.amount_available <= 0:
            raise NoAvailableMoney(f"'{new_bank_account.nick_name}' Bank Account does not have any money left.")
        if new_bank_account.amount_available < new_amount:
            raise AmountGreaterThanAvailableMoney(f"Insufficient founds from '{new_bank_account.nick_name}' bank account.")
        
        new_bank_account.amount_available -= new_amount;
    except Exception as e:
        traceback.print_exc()
        raise e