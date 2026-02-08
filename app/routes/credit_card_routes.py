from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from app.controllers import credit_card_controller as cc_controller
from app.models.credit_card import CreditCard
from app.models.expense import Expense
from app.models.bank import Bank
from app.models.bank_account import BankAccount
from app.models.credit_card_payment import CreditCardPayment
from app.utils.numeric_casting import total_amount, format_amount
from app.utils.date_handling import get_years
from app.utils.filter_data import get_not_deleted_records

credit_card_bp = Blueprint('credit_card', __name__, url_prefix='/credit_cards')

@credit_card_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.query.all()
    credit_cards = get_not_deleted_records(model=CreditCard)
    bank_accounts = BankAccount.query.all()
    years = get_years()

    context = {
        'banks': banks,
        'credit_cards': credit_cards,
        'bank_accounts': bank_accounts,
        'money_used': cc_controller.h_get_money_used_on_credit_card, #function
        'format_amount': format_amount, #function
        'total_amount': total_amount, #function
        'years': years,
    }
    return render_template('credit_cards/index.html', **context)

@credit_card_bp.route('/create', methods=['POST'])
def create():
    try:
        cc_controller.create_credit_card()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Credit card created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@credit_card_bp.route('/update', methods=['PUT'])
def update():
    try:
        credit_card_id = request.form['id']
        credit_card = CreditCard.query.get(int(credit_card_id))

        if credit_card:
            cc_controller.update_credit_card(credit_card)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Credit card created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@credit_card_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        credit_card = CreditCard.query.get(id)
        if credit_card:
            cc_controller.delete_credit_card(credit_card)
            
        return jsonify({'message': 'Credit card created successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@credit_card_bp.route('/associated_records/<int:id>', methods=['GET'])
def associated_records(id):
    credit_card = CreditCard.query.get(id)
    bank_accounts = BankAccount.query.all()
    years = get_years()
    context = {
        'credit_card': credit_card,
        'bank_accounts': bank_accounts,
        'format_amount': format_amount, #function
        'total_amount': total_amount, #function
        'years': years,
    }

    return render_template('/credit_cards/associated_records.html', **context)

@credit_card_bp.route('/associated/records/in/json/<int:id>', methods=['GET'])
def associated_records_in_json(id):
    try:
        return cc_controller.associated_records_in_json(id)
    except Exception as e:
        raise e