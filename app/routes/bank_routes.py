from flask import Blueprint, render_template, redirect, url_for

from app.controllers import bank_controller

bank_bp = Blueprint('bank', __name__, url_prefix='/banks')

@bank_bp.route('/index', methods=['GET'])
def index():
    return render_template('banks/index.html')

@bank_bp.route('/create', methods=['GET', 'POST'])
def create():
    bank = bank_controller.create_bank()
    return redirect(url_for('bank.index'))

