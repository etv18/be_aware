from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from sqlalchemy import func

from app.controllers import loan_controller
from app.controllers import loan_payment_controller
from app.models.loan import Loan
from app.models.loan_payment import LoanPayment
from app.models.bank_account import BankAccount
from app.utils.numeric_casting import format_amount, total_amount

accounts_receivable_bp = Blueprint('accounts_receivable', __name__, url_prefix='/accounts_receivable')

@accounts_receivable_bp.route('/index', methods=['GET'])
def index():
    loans = Loan.query.order_by(Loan.created_at.desc()).all()
    active_loans = Loan.query.filter(Loan.is_active == True).count()
    paid_loans = Loan.query.filter(Loan.is_active == False).count()
    remaining_to_collect = Loan.query.filter(Loan.is_active == True).with_entities(func.sum(Loan.amount)).scalar()
    bank_accounts = BankAccount.query.all()

    context = {
        'loans': loans,
        'bank_accounts': bank_accounts,
        'actives': active_loans,
        'paids': paid_loans,
        'remaining_to_collect': loan_controller.calculate_all_remainings(),
        'format_amount': format_amount,
        'total_amount': total_amount,
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
            'format_amount': format_amount,
            'total_amount': total_amount,
        }
        return render_template('accounts_receivable/associated_records.html', **context)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('loans/associated/records/in/json/<int:id>', methods=['GET'])
def associated_records_in_json(id):
    try:
        return loan_controller.associated_records_in_json(id)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    

@accounts_receivable_bp.route('/filter_loans_by_field', methods=['GET'])
def filter_loans_by_field():
    try:
        query = request.args.get('query')
        return loan_controller.filter_loans_by_field(query)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/filter_loans_by_timeframe', methods=['GET'])
def filter_loans_by_timeframe():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        return loan_controller.filter_loans_by_timeframe(start, end)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/filter/loans/all', methods=['POST'])
def filter_loans_all():
    try:
        return loan_controller.filter_all()
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

'''LOAN PAYMENTS ENDPOINTS'''

@accounts_receivable_bp.route('/create_loan_payment', methods=['POST'])
def create_loan_payment():
    try:
        return loan_payment_controller.create_loan_payment()
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/update_loan_payment/<int:loan_payment_id>', methods=['PUT'])
def update_loan_payment(loan_payment_id):
    try:
        loan_payment = LoanPayment.query.get(loan_payment_id)
        return loan_payment_controller.update_loan_payment(loan_payment)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/delete_loan_payment/<int:loan_payment_id>', methods=['DELETE'])
def delete_loan_payment(loan_payment_id):
    try:
        loan_payment = LoanPayment.query.get(loan_payment_id)
        return loan_payment_controller.delete_loan_payment(loan_payment)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
@accounts_receivable_bp.route('/see/all/loan/payments', methods=['GET'])
def see_all_loan_payments():
    try:
        context = {
            'loan_payments': LoanPayment.query.all(),
            'format_amount': format_amount,
            'total_amount': total_amount,
        }
        return render_template('accounts_receivable/loan_payments.html', **context)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400
    
    
@accounts_receivable_bp.route('/filter/loan/payments/all', methods=['POST'])
def filter_loans_payments_all():
    try:
        return loan_payment_controller.filter_all()
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400