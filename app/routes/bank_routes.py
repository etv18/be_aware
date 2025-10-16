from flask import Blueprint, render_template, redirect, url_for, request

from app.controllers import bank_controller
from app.models.bank import Bank

bank_bp = Blueprint('bank', __name__, url_prefix='/banks')

@bank_bp.route('/index', methods=['GET'])
def index():
    banks = Bank.get_all()

    return render_template('banks/index.html', banks=banks)

@bank_bp.route('/create', methods=['GET', 'POST'])
def create():
    bank = bank_controller.create_bank()

    return redirect(url_for('bank.index'))

@bank_bp.route('/update', methods=['GET', 'POST'])
def update():
    bank_id = request.form['id']
    bank = Bank.query.get(bank_id)
    if bank:
        bank_controller.update_bank(bank)
    
    return redirect(url_for('bank.index'))

@bank_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    bank = Bank.query.get(id)
    if bank:
        bank_controller.delete_bank(bank)

    return redirect(url_for('bank.index'))    

