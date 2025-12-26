from flask import request, jsonify, redirect, url_for

import traceback
from decimal import Decimal

from app.extensions import db
from app.utils.numeric_casting import is_decimal_type
from app.models.banktransfer import BankTransfer
from app.models.bank_account import BankAccount
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, BankAccountDoesNotExist, NoAvailableMoney

def create_banktransfer():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')
        
        from_bank_account_id = request.form.get('from-bank-account')
        to_bank_account_id = request.form.get('to-bank-account')

        from_bank_account = BankAccount.query.get(from_bank_account_id)
        to_bank_account = BankAccount.query.get(to_bank_account_id)

        if not from_bank_account: raise BankAccountDoesNotExist('Origin bank account was not found.')
        if not to_bank_account: raise BankAccountDoesNotExist('Destination bank account was not found.')
        if from_bank_account == to_bank_account: raise Exception('You can not select the same account.')

        h_update_bank_accounts_money_on_create(
            origin=from_bank_account,
            destination=to_bank_account,
            amount=amount
        )

        transfer = BankTransfer(
            amount=amount,
            from_bank_account_id=from_bank_account_id,
            to_bank_account_id=to_bank_account_id
        )

        db.session.add(transfer)
        db.session.commit()

        return jsonify({'message': 'Bank transfer crated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error', str(e)}), 400

def update_banktransfer(transfer):
    try:
        if not transfer: return jsonify({'error', 'Bank transfer record was not found.'})

        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')
        
        from_bank_account_id = request.form.get('from-bank-account')
        to_bank_account_id = request.form.get('to-bank-account')

        from_bank_account = BankAccount.query.get(from_bank_account_id)
        to_bank_account = BankAccount.query.get(to_bank_account_id)

        if not from_bank_account: raise BankAccountDoesNotExist('Origin bank account was not found.')
        if not to_bank_account: raise BankAccountDoesNotExist('Destination bank account was not found.')
        if from_bank_account == to_bank_account: raise Exception('You can not select the same account.')
        
        transfer.amount = amount
        transfer.from_bank_account_id = from_bank_account_id
        transfer.to_bank_account_id = to_bank_account_id
        
        return jsonify({'message': 'Bank transfer updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error', str(e)}), 400

def delete_banktransfer(transfer):
    try:
        if not transfer: return jsonify({'error', 'Bank transfer record was not found.'})
        db.session.delete(transfer)
        db.session.commit()

        return redirect(url_for('bank_account.associated_records'))
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error', str(e)}), 400
    
def h_update_bank_accounts_money_on_create(origin, destination, amount):
    if origin.amount_available <= 0 or origin.amount_available <= amount:
        raise NoAvailableMoney('Origin bank account does not have enough founds.')
    
    origin.amount_available -= amount
    destination.amount_available += amount