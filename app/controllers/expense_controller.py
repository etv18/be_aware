from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
from app.models.expense import Expense
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.exceptions.bankProductsException import *

#HANDLERS
def create_expense():
    try:
        amount = Decimal(request.form['amount'])
        is_cash = request.form.get('is-cash') == 'on'
        expense_category_id = int(request.form['select-expense-category'])
        credit_card_id = None
        bank_account_id = None
        '''
            this conditional will save either a credit_card_id or a bank_account_id
            only if you marked the expense as it wasn't made with cash, in other words...
            
            the code inside the if statement will be executed ONLY if you on the frontend 
            turn off the switcher which determines if you did or didn't use cash on the 
            transaction you just created.
        '''
        if not is_cash:
            selected_credit_card = request.form.get('select-credit-card')
            selected_bank_account = request.form.get('select-bank-account')

            if selected_credit_card and selected_credit_card != 'none':
                credit_card_id = int(request.form['select-credit-card'])
                update_credit_card_money_on_create(credit_card_id, amount)

            if selected_bank_account and selected_bank_account != 'none':
                bank_account_id = int(request.form['select-bank-account'])
                update_bank_account_money_on_create(bank_account_id, amount)

        expense = Expense(
            amount=amount,
            is_cash=is_cash,
            expense_category_id=expense_category_id,
            credit_card_id=credit_card_id,
            bank_account_id=bank_account_id
        )

        db.session.add(expense)
        db.session.commit()

    except (
        AmountGreaterThanAvailableMoney,
        BankAccountDoesNotExists,
        NoAvailableMoney
    ) as e:
        db.session.rollback()
        raise e #will automatically sends to the controller the error msg I defined before on update_bank_account_money_on_create(account_id, amount) function
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e

def update_expense(expense):
    try:
        amount = Decimal(request.form['amount'])
        is_cash = request.form.get('is-cash') == 'on'
        expense_category_id = int(request.form['select-expense-category'])
        new_credit_card_id = None
        new_bank_account_id = None
        '''
        if the expense you are updating, you edit it as it wasnt made with
        cash then the program it'll save either the credit_card_id or 
        bank_account_id
        '''
        if not is_cash:
            selected_credit_card = request.form.get('select-credit-card')
            selected_bank_account = request.form.get('select-bank-account')

            if expense.bank_account or expense.credit_card:

                old_amount = expense.amount
                new_amount = amount
                update_credit_card_or_bank_account_money_when_you_update_from_one_to_another(selected_bank_account, selected_credit_card, expense ,old_amount, new_amount)

            elif selected_credit_card and selected_credit_card != 'none':
                print('---------------------------------------------------------->>>>> 1')
                old_credit_card_id = expense.credit_card_id
                new_credit_card_id = int(request.form['select-credit-card'])
                old_amount = expense.amount #the expense object hasnt being assigned the newest amount
                new_amount = amount #newest amount from the form the user submitted
                update_credit_card_money_on_update(is_cash, old_credit_card_id, new_credit_card_id, old_amount, new_amount)

            elif selected_bank_account and selected_bank_account != 'none':
                print('---------------------------------------------------------->>>>> 2')
                old_bank_account_id = expense.bank_account_id
                new_bank_account_id = int(request.form['select-bank-account'])
                old_amount = expense.amount #the expense object hasnt being assigned the newest amount
                new_amount = amount #newest amount from the form the user submitted
                update_bank_account_money_on_update(is_cash, old_bank_account_id, new_bank_account_id, old_amount, new_amount)

            else:
                print('---------------------------------------------------------->>>>> 3')
                old_amount = expense.amount
                new_amount = amount
                update_credit_card_or_bank_account_money_when_you_update_from_one_to_another(expense, old_amount, new_amount)

        expense.amount = amount
        expense.is_cash = is_cash
        expense.expense_category_id = expense_category_id
        expense.credit_card_id = new_credit_card_id
        expense.bank_account_id = new_bank_account_id

        db.session.commit()
    except (
        AmountGreaterThanAvailableMoney,
        BankAccountDoesNotExists,
        NoAvailableMoney
    ) as e:
        db.session.rollback()
        raise e #will automatically sends to the controller the error msg I defined before on update_bank_account_money_on_create(account_id, amount) function
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e 

def delete_expense(expense):
    if request.method == 'POST':
        db.session.delete(expense)
        db.session.commit()

def filter_by_time(start, end):
    data_from_database = []

    try:

        if not start or not end:
            return jsonify({'error', 'Missing date range'}), 400
        
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        end_date += timedelta(days=1)

        expenses = Expense.query.filter(
            Expense.created_at.between(start_date, end_date)
        ).all()

        for e in expenses:
            data_from_database.append(e.to_dict())

    except Exception as e:
        print(e)
    
    return data_from_database

def weekly_basis_expenses_info():
    start_date, end_date = get_current_week_range()
    
    expenses = (
        Expense.query
        .filter(Expense.created_at >= start_date)
        .filter(Expense.created_at <= end_date)
        .order_by(Expense.created_at.desc())
        .all()
    )

    data = []
    
    for e in expenses:
        data.append(e)
    
    return data

#HELPER FUNCTIONS
def get_current_week_range():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week.date(), end_of_week.date()

def money_limit_spent_left_for_expenses(expenses):
    spent = Decimal()
    for e in expenses:
        spent += e.amount

    limit = Decimal(3300) #Right now the limit will be hard coded I need to add a new column to expense_category model so I can know the exact amount
    
    left = Decimal(limit - spent)

    weekly = {
        'limit': limit,
        'spent': spent,
        'left': left,
    }

    return weekly

def update_bank_account_money_on_create(id, amount):
    bank_account = BankAccount.query.get(id)

    if not bank_account:
        raise BankAccountDoesNotExists('This bank account does not exists.')
    if bank_account.amount_available <= 0:
        raise NoAvailableMoney('Bank Account does not have any money left.')
    if bank_account.amount_available < amount:
        raise AmountGreaterThanAvailableMoney('Insufficient founds.')
    
    bank_account.amount_available -= amount

def update_credit_card_money_on_create(id, amount):
    credit_card = CreditCard.query.get(id)

    if not credit_card:
        raise CreditCardDoesNotExists('This credit card does not exists.')
    if credit_card.amount_available <= 0:
        raise NoAvailableMoney('Credit card does not have any money left.')
    if credit_card.amount_available < amount:
        raise AmountGreaterThanAvailableMoney('Insufficient founds.')
    
    credit_card.amount_available -= amount

def update_bank_account_money_on_update(is_cash, old_ba_id, new_ba_id, old_amount, new_amount):
    old_bank_account = None
    new_bank_account = None

    try:
        if old_ba_id: #if the bank account id is true it means it's bank account to bank account transaction
            old_bank_account = BankAccount.query.get(old_ba_id)
            if not old_bank_account:
                raise BankAccountDoesNotExists('Bank account does not exists.')   
            old_bank_account.amount_available += old_amount; #refund the money used to the previous bank account
        
        new_bank_account = BankAccount.query.get(new_ba_id)

        if not new_bank_account:
            raise BankAccountDoesNotExists('Bank account does not exists.')
        if new_bank_account.amount_available <= 0:
            raise NoAvailableMoney('Bank Account does not have any money left.')
        if new_bank_account.amount_available < new_amount:
            raise AmountGreaterThanAvailableMoney('Insufficient founds.')
        
        new_bank_account.amount_available -= new_amount;
    except Exception as e:
        print('Error message: ', e)
        traceback.print_exc(e)
    
def update_credit_card_money_on_update(is_cash, old_cc_id, new_cc_id, old_amount, new_amount):
    old_credit_card = None
    new_credit_card = None

    try:
        if old_cc_id:
            old_credit_card = CreditCard.query.get(old_cc_id)
            if not old_credit_card:
                raise CreditCardDoesNotExists('This credit card does not exists.')
            old_credit_card.amount_available += old_amount
    
        new_credit_card = CreditCard.query.get(new_cc_id)

        if not new_credit_card:
            raise CreditCardDoesNotExists('This credit card does not exists.')
        if new_credit_card.amount_available <= 0:
            raise NoAvailableMoney('Credit card does not have any money left.')
        if new_credit_card.amount_available < new_amount:
            raise AmountGreaterThanAvailableMoney('Insufficient founds.')
        
        new_credit_card.amount_available -= new_amount
    except Exception as e:
        print('Error message: ', e)
        traceback.print_exc(e)

def update_credit_card_or_bank_account_money_when_you_update_from_one_to_another(selected_bank_account, selected_credit_card, expense, old_amount, new_amount):
        bank_account = None
        credit_card = None
        bank_account_id = 0
        credit_card_id = 0

        if selected_bank_account and selected_bank_account != 'none':
            bank_account_id = int(request.form['select-bank-account'])
            bank_account = BankAccount.query.get(bank_account_id)
        else:
            credit_card_id = int(request.form['select-credit-card'])
            credit_card = CreditCard.query.get(credit_card_id)

        try:
            if expense.bank_account_id: #if its true it means the transaction was first made from a bank account and it'll be updated to be an expense made with a credit card
                expense.bank_account.amount_available += old_amount
                credit_card.amount_available -= new_amount
            else: 
                expense.credit_card.amount_available += old_amount
                bank_account.amount_available -= new_amount
        except Exception as e:
            print('Error message: ')
            traceback.print_exc(e)