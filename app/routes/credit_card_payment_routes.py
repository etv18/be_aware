from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from app.controllers import credit_card_payment_controller
from app.models.credit_card_payment import CreditCardPayment

credit_card_payment_bp = Blueprint('credit_card_payment', __name__, url_prefix='/credit_card_payments')

@credit_card_payment_bp.route('/create', methods=['POST'])
def create():
    try:
        return credit_card_payment_controller.create_credit_card_payment()
    except Exception as e:
        print(e)
        raise e 