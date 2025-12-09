from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from app.controllers import credit_card_controller as cc_controller
from app.models.credit_card import CreditCard
from app.models.expense import Expense
from app.models.bank import Bank
from app.models.bank_account import BankAccount
from app.models.credit_card_payment import CreditCardPayment

credit_card_bp = Blueprint('credit_card', __name__, url_prefix='/credit_cards')

@credit_card_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.query.all()
    credit_cards = CreditCard.query.all()
    bank_accounts = BankAccount.query.all()

    context = {
        'banks': banks,
        'credit_cards': credit_cards,
        'bank_accounts': bank_accounts,
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
    expenses = (
        Expense.query
        .filter(Expense.credit_card_id == id)
        .order_by(Expense.created_at.desc())
        .all()
    )
    bank_accounts = BankAccount.query.all()
    payments = CreditCardPayment.query.filter(CreditCardPayment.credit_card_id == id).all()
    context = {
        'expenses': expenses,
        'bank_accounts': bank_accounts,
        'payments': payments,
    }

    return render_template('/credit_cards/associated_records.html', **context)

