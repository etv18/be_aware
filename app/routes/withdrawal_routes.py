from flask import Blueprint, jsonify, request, render_template

from app.controllers import withdrawal_controller
from app.models.withdrawal import Withdrawal
from app.models.bank_account import BankAccount

withdrawal_bp = Blueprint('withdrawal', __name__, url_prefix='/withdrawals')

@withdrawal_bp.route('index', methods=['GET'])
def index():
    withdrawals = Withdrawal.query.all()
    bank_accounts = BankAccount.query.all()
    context = {
        'withdrawals': withdrawals,
        'bank_accounts': bank_accounts,
    }
    return render_template('withdrawals/index.html', **context)

@withdrawal_bp.route('/create', methods=['POST'])
def create():
    try:
        withdrawal_controller.create_withdrawal()
        return jsonify({'message': 'Withdrawal created successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@withdrawal_bp.route('/update/<int:id>', methods=['PUT'])
def update(id):
    try:
        withdrawal_controller.update_withdrawal(id)
        return jsonify({'message': 'Withdrawal updated successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@withdrawal_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        withdrawal_controller.delete_withdrawal(id)
        return jsonify({'message': 'Withdrawal deleted successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@withdrawal_bp.route('/filter_withdrawals_by_field', methods=['GET'])
def filter_withdrawals_by_field():
    try:
        query = request.args.get('query')
        print(query)
        withdrawals = withdrawal_controller.filter_withdrawals_by_field(query)
        return jsonify({'withdrawals': withdrawals}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400