from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from decimal import Decimal

from app.controllers import bank_account_controller as ba_controller
from app.models.bank_account import BankAccount
from app.models.bank import Bank


bank_account_bp = Blueprint('bank_account', __name__, url_prefix='/bank_accounts')

@bank_account_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.query.all()
    bank_accounts = BankAccount.query.all()
    total_money = Decimal()

    for account in bank_accounts:
        total_money += account.amount_available

    total_money_formatted = f'{total_money:,.2f}'

    context = {
        'banks': banks,
        'bank_accounts': bank_accounts,
        'total_money': total_money_formatted,
    }

    return render_template('bank_accounts/index.html', **context)

@bank_account_bp.route('/create', methods=['GET', 'POST'])
def create():
    try:
        ba_controller.create_bank_account()
        return jsonify({'message': 'Bank account created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bank_account_bp.route('/update', methods=['PUT'])
def update():
    try:
        bank_account_id = request.form['id']
        bank_account = BankAccount.query.get(int(bank_account_id))

        if bank_account:
            ba_controller.update_bank_account(bank_account)
            
        return jsonify({'message': 'Bank account edited successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bank_account_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        bank_account = BankAccount.query.get(id)
        if bank_account:
            ba_controller.delete_bank_account(bank_account)

        return jsonify({'message': 'Bank account edited successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bank_account_bp.route('/associated_records/<int:bank_account_id>')
def associated_records(bank_account_id):
    try:
        data = ba_controller.get_associated_records(bank_account_id)
        return render_template('bank_accounts/associated_records.html', **data)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    