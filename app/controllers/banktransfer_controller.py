from flask import request, jsonify, redirect, url_for

import traceback
from decimal import Decimal

from app.extensions import db
from app.utils.numeric_casting import is_decimal_type
from app.models.banktransfer import BankTransfer
from app.models.bank_account import BankAccount
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.exceptions.bankProductsException import AmountIsLessThanOrEqualsToZero, BankAccountDoesNotExists, NoAvailableMoney

def create_banktransfer():
    try:
        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a valid number bigger than 0')
        
        from_bank_account_id = request.form.get('from-bank-account')
        to_bank_account_id = request.form.get('to-bank-account-select')

        from_bank_account = BankAccount.query.get(from_bank_account_id)
        to_bank_account = BankAccount.query.get(to_bank_account_id)

        if not from_bank_account: raise BankAccountDoesNotExists('Origin bank account was not found.')
        if not to_bank_account: raise BankAccountDoesNotExists('Destination bank account was not found.')
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

        BankAccountTransactionsLedger.create(transfer)

        return jsonify({'message': 'Bank transfer crated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

def update_banktransfer(id):
    try:
        transfer = BankTransfer.query.get(id)
        if not transfer: return jsonify({'error', 'Bank transfer record was not found.'}), 400

        amount = Decimal(request.form.get('amount')) if is_decimal_type(request.form.get('amount')) else Decimal('0')
        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')
        
        to_bank_account_id = request.form.get('to-bank-account-select')
        to_bank_account = BankAccount.query.get(to_bank_account_id)
        if not to_bank_account: raise BankAccountDoesNotExists('Destination bank account was not found.')
        
        h_update_bank_accounts_money_on_update(
            origin=transfer.from_bank_account,
            old_destination=transfer.to_bank_account,
            new_destination=to_bank_account,
            old_amount=transfer.amount,
            new_amount=amount
        )
        transfer.amount = amount
        transfer.to_bank_account_id = to_bank_account_id
        
        db.session.commit()

        BankAccountTransactionsLedger.update(transfer)
        return jsonify({'message': 'Bank transfer updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

def delete_banktransfer(id):
    try:
        transfer = BankTransfer.query.get(id)
        if not transfer: return jsonify({'error', 'Bank transfer record was not found.'}), 400
        h_update_bank_accounts_money_on_delete(transfer)

        BankAccountTransactionsLedger.delete(transfer)
        
        db.session.delete(transfer)
        db.session.commit()

        return jsonify({'message': 'Bank transfer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def get_record(id):
    try:
        transfer = BankTransfer.query.get(id)
        return jsonify({'transfer': transfer.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def h_update_bank_accounts_money_on_create(origin, destination, amount):
    if origin.amount_available <= 0 or origin.amount_available < amount:
        raise NoAvailableMoney('Origin bank account does not have enough founds.')
    
    origin.amount_available -= amount
    destination.amount_available += amount

def h_update_bank_accounts_money_on_update(origin, old_destination, new_destination, old_amount, new_amount):

    if old_destination.amount_available <= 0 or old_destination.amount_available < old_amount:
        raise NoAvailableMoney(f'{old_destination.nick_name.capitalize()} does not have enough founds.')
    
    old_destination.amount_available -= old_amount #take the money which was transfered to the old destination bank account
    
    origin.amount_available += old_amount #return the money transfered to the origin bank account

    if origin.amount_available <= 0 or origin.amount_available < new_amount:
        raise NoAvailableMoney(f'{origin.nick_name.capitalize()} does not have enough founds.')
    
    origin.amount_available -= new_amount
    new_destination.amount_available += new_amount

def h_update_bank_accounts_money_on_delete(transfer):
    if transfer.to_bank_account.amount_available <= 0 or transfer.to_bank_account.amount_available < transfer.amount:
        raise NoAvailableMoney(f'{transfer.to_bank_account.nick_name.capitalize()} does not have enough founds.')
    
    transfer.to_bank_account.amount_available -= transfer.amount #takes the transfered money from the destination
    transfer.from_bank_account.amount_available += transfer.amount #return the money to its origin
