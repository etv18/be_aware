from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from app.controllers import credit_card_payment_controller
from app.models.credit_card_payment import CreditCardPayment

credit_card_payment_bp = Blueprint('credit_card_payment', __name__, url_prefix='/credit_card_payments')

@credit_card_payment_bp.route('/create', methods=['POST'])
def create():
    try:
        credit_card_payment_controller.create_credit_card_payment()
        return jsonify({'message': 'Credit card payment created successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@credit_card_payment_bp.route('/update/<int:id>', methods=['PUT'])
def update(id):
    try:
        credit_card_payment_controller.update_credit_card_payment(id)
        return jsonify({'message': 'Credit card payment updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@credit_card_payment_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        credit_card_payment_controller.delete_credit_card_payment(id)
        return jsonify({'message': 'Credit card payment updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400