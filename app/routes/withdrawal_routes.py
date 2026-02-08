from flask import Blueprint, jsonify, request, render_template

from app.controllers import withdrawal_controller
from app.models.withdrawal import Withdrawal
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import format_amount, total_amount
from app.utils.date_handling import get_years
from app.utils.filter_data import get_not_deleted_records

withdrawal_bp = Blueprint('withdrawal', __name__, url_prefix='/withdrawals')

@withdrawal_bp.route('index', methods=['GET'])
def index():
    withdrawals = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    bank_accounts = get_not_deleted_records(model=BankAccount)
    years = get_years()
    context = {
        'withdrawals': withdrawals,
        'bank_accounts': bank_accounts,
        'total_amount': total_amount,
        'format_amount': format_amount,
        'years': years,
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
        return withdrawal_controller.filter_withdrawals_by_field(query)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@withdrawal_bp.route('/filter/withdrawals/by/timeframe', methods=['GET'])
def filter_withdrawals_by_timeframe():
    try:
        start = request.args.get('start')
        end =request.args.get('end')
        return withdrawal_controller.filter_withdrawals_by_timeframe(start, end)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@withdrawal_bp.route('/filter/all', methods=['POST'])
def filter_all():
    try:
        return withdrawal_controller.filter_all()
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400