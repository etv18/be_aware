from flask import request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
import traceback

from app.exceptions.bankProductsException import BankAccountDoesNotExists, AmountIsLessThanOrEqualsToZero
from app.extensions import db
from app.utils.bank_accounts.filter_data import get_yearly_total_amount_info, get_yearly_total_amount_info_of_transfers
from app.utils.numeric_casting import is_decimal_type, total_amount, format_amount
from app.models.bank_account import BankAccount
from app.models.expense import Expense
from app.models.bank import Bank
from app.models.loan_payment import LoanPayment
from app.models.loan import Loan
from app.models.withdrawal import Withdrawal
from app.models.credit_card_payment import CreditCardPayment
from app.models.income import Income
from app.models.banktransfer import BankTransfer

def create_bank_account():
    try:
        if request.method == 'POST':
            nick_name = request.form['nick-name']
            amount_available = Decimal(request.form['amount-available']) if is_decimal_type(request.form['amount-available']) else Decimal('0')
            account_number = request.form['account-number']
            bank_id = int(request.form['select-banks'])

            if(amount_available <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce valid number bigger than 0')

            bank_account = BankAccount(
                nick_name=nick_name,
                amount_available=amount_available,
                account_number=account_number,
                bank_id=bank_id
            )

            db.session.add(bank_account)
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def update_bank_account(bank_account):
    try:
        if request.method == 'PUT':
            bank_account.nick_name = request.form['e-nick-name'];
            bank_account.account_number = request.form['e-account-number'];
            bank_account.amount_available = Decimal(request.form['e-amount-available']) if is_decimal_type(request.form['e-amount-available']) else Decimal('0')

            if(bank_account.amount_available <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce valid number bigger than 0')

            bank_id = request.form['e-select-banks'];
            bank_account.bank_id = int(bank_id)

            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def delete_bank_account(bank_account):
    try:        
        db.session.delete(bank_account)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e
    except Exception as e:
        db.session.rollback()
        raise e

def get_associated_records(bank_account_id):
    try:
        data = {}
        bank_account = BankAccount.query.get(bank_account_id)
        bank_accounts = BankAccount.query.all()
        banktransfers = (
            BankTransfer.query.filter(
                (BankTransfer.from_bank_account_id == bank_account.id) |
                (BankTransfer.to_bank_account_id == bank_account.id)
            )
            .order_by(BankTransfer.created_at.desc())
            .all()
        )
        data = {
            'bank_account': bank_account,
            'all_bank_accounts': bank_accounts,
            'banktransfers': banktransfers,
            'total_amount': total_amount, #this the utility function to transfor decimal objects into a readable currency string
            'format_amount': format_amount,
        }
        return data
    except BankAccountDoesNotExists as e:
        raise BankAccountDoesNotExists('Bank account does not exists.')
    except Exception as e:
        raise e
    
def get_associated_records_in_json(bank_account_id):
    try:
        bank_account = BankAccount.query.get(bank_account_id)
        if not bank_account: 
            return jsonify({'error': 'Bank account not found'}), 404

        '''
        This will query transfer where the bank account id is either
        on from_bank_account_id or to_bank_account_id column on the DB
        '''
        banktransfers = BankTransfer.query.filter(
            (BankTransfer.from_bank_account_id == bank_account.id) |
            (BankTransfer.to_bank_account_id == bank_account.id)
        ).all()

        associations = [
            bank_account.expenses,
            bank_account.incomes,
            bank_account.loans,
            bank_account.loan_payments,
            bank_account.credit_card_payments,
            bank_account.withdrawals,
            banktransfers
        ]
        data = {}
        for a in associations:
            if a:
                table_name = a[0].__class__.__tablename__; '''access the first element to get its table name'''
                data[table_name] = h_get_data_as_dictionary(a); '''set the table name as the key and use the function to  get all elements of the list in dictionary format'''
        
        return jsonify({
            'owner_bank_account_id': bank_account.id,
            'records': data
            }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
def get_cash_flow_info(bank_account_id, year=None):

    outgoing_classes = [Expense, Withdrawal, Loan, CreditCardPayment]
    incoming_classes = [LoanPayment, Income]

    #Since transfer's stores outgoings and incomings cash flow they have to be
    #managed individually to get each group separetly
    transfers = get_yearly_total_amount_info_of_transfers(id=bank_account_id, year=year)

    outgoings = h_get_total_amount_info_using_models(
        id=bank_account_id, 
        models=outgoing_classes,
        transfers=transfers.get('outgoings'),
        year=year
    )

    incomings = h_get_total_amount_info_using_models(
        id=bank_account_id, 
        models=incoming_classes,
        transfers=transfers.get('incomings'),
        year=year
    )

    balances = h_get_balances(outgoings=outgoings, incomings=incomings)

    data = {
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'outgoings': outgoings,
        'incomings': incomings,
        'balances': balances
    }
    return jsonify(data), 200


def h_get_balances(outgoings: list, incomings: list):
    balances = []
    for month in range(0, 12):
        balances.append(
            incomings[month] - outgoings[month] 
        )
    return balances
        


def h_get_total_amount_info_using_models(id, models: list, transfers: list, year=None) -> list:
    year_results = []
    for model in models:
        totals = get_yearly_total_amount_info(
            id=id,
            CustomModel=model,
            year=year
        )
        year_results.append(totals)
    '''
    Since transfer's stores outgoings and incomings cash flow they have to be
    managed individually to get each group separetly
    '''
    year_results.append(transfers)
    total_amounts_per_month = [Decimal('0.00') for _ in range(12)]

    for model_info in year_results:
        for i in range(0, len(model_info)):
            total_amounts_per_month[i] += model_info[i]

    return total_amounts_per_month



def h_get_data_as_dictionary(elems: list) -> list:
    if not elems: return

    container = []
    for e in elems:
        container.append(e.to_dict())
    return container

