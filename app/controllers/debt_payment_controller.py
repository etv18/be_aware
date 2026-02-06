from flask import request, jsonify

from decimal import Decimal
import traceback
from datetime import datetime, timedelta

from app.extensions import db
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.debt_payment import DebtPayment
from app.models.debt import Debt
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import is_decimal_type, total_amount
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
        
        if debt_payment.is_cash         :  CashLedger.create(debt_payment)
        if debt_payment.bank_account_id : BankAccountTransactionsLedger.create(debt_payment)

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

        CashLedger.update_or_delete(debt_payment)
        BankAccountTransactionsLedger.update(debt_payment)

        _update_debt_is_active(debt)

        return jsonify({'message': 'Debt payment updated successfully'}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def delete(id):
    try:
        debt_payment = DebtPayment.query.get(id)
        if not debt_payment:
            return jsonify({'error': 'Debt payment record was not found'}), 400
        
        debt = Debt.query.get(debt_payment.debt_id)

        if debt_payment.bank_account:
            debt_payment.bank_account.amount_available += debt_payment.amount
            BankAccountTransactionsLedger.delete(debt_payment)

        CashLedger.update_or_delete(debt_payment, delete_ledger=True)

        db.session.delete(debt_payment)
        db.session.commit()

        _update_debt_is_active(debt)

        return jsonify({'message': 'Debt payment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def filter_all():
    try:
        data = request.get_json(silent=True) or {}

        query = data.get('query')
        start = data.get('start')
        end = data.get('end')

        if not query and (not start or not end):
            return jsonify({
                'error': 'Try to type some query or select a time frame.'
            }), 400

        and_filters = []

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            end_date += timedelta(days=1)
            and_filters.append(DebtPayment.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'

            is_cash = _evaluate_boolean_columns(query, 'yes', 'no')    
            is_active = _evaluate_boolean_columns(query, 'active', 'paid')

            if is_cash is not None:
                and_filters.append(DebtPayment.is_cash == is_cash)
            elif is_active is not None:
                and_filters.append(DebtPayment.is_active == is_active)
            else:
                text_filters = db.or_(
                    (DebtPayment.amount.ilike(q)),
                    (DebtPayment.code.ilike(q)),
                    (BankAccount.nick_name.ilike(q))
                )

                and_filters.append(text_filters)

        debt_payments = (
            DebtPayment.query
            .outerjoin(DebtPayment.bank_account) #allows to show expense without a bank account        
            .filter(db.and_(*and_filters))
            .order_by(DebtPayment.created_at.desc())
            .all()
        )

        debt_payment_list = []
        for l in debt_payments:
            debt_payment_list.append(l.to_dict())
        
        return jsonify({
            'debt_payments': debt_payment_list,
            'total': total_amount(debt_payments)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500  

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
    
def _evaluate_boolean_columns(query, reference_for_true, reference_for_false):
    q = query.lower()
    if q == reference_for_true.lower():
        return True
    if q == reference_for_false.lower():
        return False
    return None