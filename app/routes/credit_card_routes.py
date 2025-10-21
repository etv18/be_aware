from flask import Blueprint, render_template, redirect, url_for, request

from app.controllers import credit_card_controller as cc_controller
from app.models.credit_card import CreditCard
from app.models.bank import Bank

credit_card_bp = Blueprint('credit_card', __name__, url_prefix='/credit_cards')

@credit_card_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.query.all()
    credit_cards = CreditCard.query.all()
    context = {
        'banks': banks,
        'credit_cards': credit_cards
    }
    return render_template('credit_cards/index.html', **context)

@credit_card_bp.route('/create', methods=['POST'])
def create():
    cc_controller.create_credit_card()

    return redirect(url_for('credit_card.index'))