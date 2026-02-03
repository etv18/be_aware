from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
from app.models.bank_account import BankAccount
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.loan import Loan
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero
from app.controllers.income_controller import update_bank_account_money_on_create, update_bank_account_money_on_update, update_bank_account_money_on_delete
from app.models.loan_payment import LoanPayment
from app.utils.numeric_casting import is_decimal_type, format_amount, total_amount

def create_loan_payment():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        bank_account_id = None
        loan_id = int(request.form['loan-id'])

        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400

        if loan.total_payments() >= loan.amount:
            return jsonify({
                'message': 'Loan is already fully paid',
                'is_paid': True
            }), 200
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        if not is_cash:
            bank_account_id = request.form.get('select-bank-account')
            update_bank_account_money_on_create(bank_account_id, amount)

        loan_payment = LoanPayment(
            amount=amount,
            is_cash=is_cash,
            bank_account_id=bank_account_id,
            loan_id=loan_id
        )
        db.session.add(loan_payment)
        db.session.commit()
        
        CashLedger.create(loan_payment)
        if loan_payment.bank_account_id: BankAccountTransactionsLedger.create(loan_payment)

        update_loan_is_active(loan)

        return jsonify({'message': 'Loan payment created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e


def update_loan_payment(loan_payment):
    try:
        if not loan_payment:
            return jsonify({'error': 'Loan payment record was not found'}), 400
        
        new_amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
 
        new_bank_account_id = None
        is_cash = request.form.get('is-cash') == 'on'
        selected_bank_account = request.form.get('select-bank-account')
        loan_id = int(request.form['loan-id'])
        
        
        if(new_amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400

        #expected_total_payments = (loan.total_payments() - loan_payment.amount) + new_amount
        #if expected_total_payments > loan.amount:
        #    return jsonify({
        #        'message': 'The updated amount exceeds the remaining loan balance',
        #        'is_paid': True
        #    }), 200
        
        if not is_cash and (selected_bank_account != None or selected_bank_account != '' or selected_bank_account != 'none'):
            new_bank_account_id = int(request.form.get('select-bank-account'))
            new_bank_account = BankAccount.query.get(new_bank_account_id)
            update_bank_account_money_on_update(loan_payment.bank_account, new_bank_account, loan_payment.amount, new_amount)
        elif loan_payment.bank_account:
            loan_payment.bank_account.amount_available -= loan_payment.amount

        loan_payment.amount = new_amount
        loan_payment.is_cash = is_cash
        loan_payment.bank_account_id = new_bank_account_id

        db.session.commit()

        CashLedger.update_or_delete(loan_payment)
        BankAccountTransactionsLedger.update(loan_payment)

        update_loan_is_active(loan)
        return jsonify({'message': 'Loan payment created successfully'}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e
    
def delete_loan_payment(loan_payment):
    try:
        if not loan_payment:
            return jsonify({'error': 'Loan payment record was not found'}), 400
        
        loan = loan_payment.loan
        if loan_payment.bank_account:
            update_bank_account_money_on_delete(loan_payment.bank_account, loan_payment.amount)
            BankAccountTransactionsLedger.delete(loan_payment)

        CashLedger.update_or_delete(loan_payment, delete_ledger=True)

        db.session.delete(loan_payment)
        db.session.commit()

        update_loan_is_active(loan)

        return jsonify({'message': 'Loan payment deleted successfully'}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def update_loan_is_active(loan):
    db.session.refresh(loan)  # <-- refresh from DB
    loan.is_active = loan.remaining_amount() > 0
    db.session.commit()

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
            and_filters.append(LoanPayment.created_at.between(start_date, end_date))

        if query: 
            q = f'%{query}%'

            is_cash = evaluate_boolean_columns(query, 'yes', 'no')    
            is_active = evaluate_boolean_columns(query, 'active', 'paid')

            if is_cash is not None:
                and_filters.append(LoanPayment.is_cash == is_cash)
            elif is_active is not None:
                and_filters.append(LoanPayment.is_active == is_active)
            else:
                text_filters = db.or_(
                    (LoanPayment.amount.ilike(q)),
                    (LoanPayment.code.ilike(q)),
                    (BankAccount.nick_name.ilike(q))
                )

                and_filters.append(text_filters)

        loan_payments = (
            LoanPayment.query
            .outerjoin(LoanPayment.bank_account) #allows to show expense without a bank account        
            .filter(db.and_(*and_filters))
            .order_by(LoanPayment.created_at.desc())
            .all()
        )

        loan_payment_list = []
        for l in loan_payments:
            loan_payment_list.append(l.to_dict())
        
        return jsonify({
            'loan_payments': loan_payment_list,
            'total': total_amount(loan_payments)
        }), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500  
    
def evaluate_boolean_columns(query, reference_for_true, reference_for_false):
    q = query.lower()
    if q == reference_for_true.lower():
        return True
    if q == reference_for_false.lower():
        return False
    return None