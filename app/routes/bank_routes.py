from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, logout_user, login_required

from app.controllers import bank_controller
from app.models.bank import Bank

bank_bp = Blueprint('bank', __name__, url_prefix='/banks')

@bank_bp.route('/index', methods=['GET'])
@login_required
def index():
    banks = Bank.query.all()

    return render_template('banks/index.html', banks=banks)

@bank_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    bank_controller.create_bank()

    return redirect(url_for('bank.index'))

@bank_bp.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    bank_id = request.form['id']
    bank = Bank.query.get(bank_id)
    if bank:
        bank_controller.update_bank(bank)
    
    return redirect(url_for('bank.index'))

@bank_bp.route('/delete/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        bank = Bank.query.get(id)
        if bank:
            bank_controller.delete_bank(bank)
            
        return jsonify({'message': 'Bank account edited successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

