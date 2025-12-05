from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from app.controllers import loan_controller
from app.controllers import loan_payment_controller
from app.models.loan import Loan
from app.models.loan_payment import LoanPayment
from app.models.bank_account import BankAccount

accounts_receivable_bp = Blueprint('accounts_receivable', __name__, url_prefix='/accounts_receivable')

@accounts_receivable_bp.route('/index', methods=['GET'])
def index():
    loans = Loan.query.all()
    bank_accounts = BankAccount.query.all()
    context = {
        'loans': loans,
        'bank_accounts': bank_accounts,
    }
    return render_template('accounts_receivable/index.html', **context)

@accounts_receivable_bp.route('/create_loan', methods=['POST'])
def create_loan():
    try:
        loan_controller.create_loan()
        return jsonify({'message': 'Loan created successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/update_loan/<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        return loan_controller.update_loan(loan)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/delete/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        return loan_controller.delete_loan(loan)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('associated_records/<int:loan_id>', methods=['GET'])
def associated_records(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        bank_accounts = BankAccount.query.all()

        if not loan:
            return jsonify({'error': 'Loan record was not found'}), 400
        context = {
            'loan': loan,
            'bank_accounts': bank_accounts,
        }
        return render_template('accounts_receivable/associated_records.html', **context)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/create_loan_payment', methods=['POST'])
def create_loan_payment():
    try:
        return loan_payment_controller.create_loan_payment()
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400