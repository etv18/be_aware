from flask import request, jsonify, redirect, url_for

import traceback
from datetime import datetime, timedelta
from decimal import Decimal

from app.extensions import db
from app.models.debt import Debt
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, NoBankProductSelected, AmountGreaterThanAvailableMoney, NoAvailableMoney, BankAccountDoesNotExists
from app.utils.numeric_casting import is_decimal_type

def create():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        person_name = request.form.get('person-name')
        description = request.form.get('description')
        bank_account_id = None
        
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        selected_bank_account_id = request.form.get('select-bank-account')
    

        if not is_cash:
            if selected_bank_account_id == 'none' or not selected_bank_account_id:
                raise NoBankProductSelected('No bank account was selected for this debt')
            
            bank_account_id = int(selected_bank_account_id)
            add_money_to_back_account(bank_account_id, amount)

        debt = Debt(
            amount=amount,
            is_cash=is_cash,
            person_name=person_name,
            bank_account_id=bank_account_id,
            description=description
        )

        db.session.add(debt)
        db.session.commit()

        #CashLedger.create(debt)
        #if debt.bank_account_id: BankAccountTransactionsLedger.create(debt)

        return jsonify({'message': 'Loan created successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def add_money_to_back_account(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    
    bank_account.amount_available += amount