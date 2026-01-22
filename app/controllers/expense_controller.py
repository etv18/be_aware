from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_

from decimal import Decimal
from datetime import datetime, timedelta
import traceback

from app.extensions import db
from app.models.expense import Expense
from app.models.expense_category import ExpenseCategory
from app.models.bank_account import BankAccount
from app.models.credit_card import CreditCard
from app.models.cash_ledger import CashLedger
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.exceptions.bankProductsException import *
from app.utils.numeric_casting import is_decimal_type, total_amount

#HANDLERS
def create_expense():
    try:
        amount = Decimal(request.form['amount']) if is_decimal_type(request.form['amount']) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        expense_category_id = int(request.form['select-expense-category'])
        description = request.form.get('description')
        credit_card_id = None
        bank_account_id = None

        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

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

            if (not selected_credit_card or selected_credit_card == 'none') and (not selected_bank_account or selected_bank_account == 'none'):
                raise NoBankProductSelected('You must select either a credit card or bank account.')

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
            bank_account_id=bank_account_id,
            description=description
        )


        db.session.add(expense)
        db.session.commit()

        CashLedger.create(expense)
        if expense.bank_account_id: BankAccountTransactionsLedger.create(expense)


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
        amount = Decimal(request.form['amount']) if is_decimal_type(request.form['amount']) else Decimal('0')
        is_cash = request.form.get('is-cash') == 'on'
        expense_category_id = int(request.form['select-expense-category'])
        description = request.form.get('description')
        print(f'value {expense_category_id} of {type(expense_category_id)}')
        new_credit_card_id = None
        new_bank_account_id = None

        if(amount <= 0): raise AmountIsLessThanOrEqualsToZero('Introduce a number bigger than 0')

        '''
        if the expense you are updating, you edit it as it wasnt made with
        cash then the program it'll save either the credit_card_id or 
        bank_account_id
        '''
        if not is_cash:
            selected_credit_card = request.form.get('select-credit-card')
            selected_bank_account = request.form.get('select-bank-account')

            #Current expense object
            current_has_bank_acnt = expense.bank_account is not None 
            current_has_credit_card = expense.credit_card is not None
            #Update for expense object 
            update_has_bank_acnt = selected_bank_account and selected_bank_account != 'none'
            update_has_credit_card = selected_credit_card and selected_credit_card != 'none'

            print(f'bank account {update_has_bank_acnt} {type(update_has_bank_acnt)}')
            print(f'credit card {update_has_credit_card} {type(update_has_credit_card)}')

            if not update_has_credit_card and not update_has_bank_acnt:
                raise NoBankProductSelected('You must select either a credit card or bank account.')

            if (current_has_bank_acnt and not update_has_bank_acnt) or (current_has_credit_card and not update_has_credit_card):
                old_amount = expense.amount
                new_amount = amount

                #assign the new bankproduct id so the swap between each bank products can be register into the database
                if not current_has_bank_acnt:
                    new_bank_account_id = int(request.form['select-bank-account'])
                else:
                    new_credit_card_id = int(request.form['select-credit-card'])

                update_credit_card_or_bank_account_money_when_you_update_from_one_to_another(selected_bank_account, selected_credit_card, expense ,old_amount, new_amount)
                print('%%%%%%%%%%%%%%%%%%%%%%%%%======> 1')

            elif selected_credit_card and selected_credit_card != 'none':
                old_credit_card_id = expense.credit_card_id
                new_credit_card_id = int(request.form['select-credit-card'])
                old_amount = expense.amount #the expense object hasnt being assigned the newest amount
                new_amount = amount #newest amount from the form the user submitted
                update_credit_card_money_on_update(is_cash, old_credit_card_id, new_credit_card_id, old_amount, new_amount)
                print('%%%%%%%%%%%%%%%%%%%%%%%%%======> 2')

            elif selected_bank_account and selected_bank_account != 'none':
                old_bank_account_id = expense.bank_account_id
                new_bank_account_id = int(request.form['select-bank-account'])
                old_amount = expense.amount #the expense object hasnt being assigned the newest amount
                new_amount = amount #newest amount from the form the user submitted
                update_bank_account_money_on_update(old_bank_account_id, new_bank_account_id, old_amount, new_amount)
                print('%%%%%%%%%%%%%%%%%%%%%%%%%======> 3')

        elif expense.credit_card or expense.bank_account: 
            return_money(expense)
 
        expense.amount = amount
        expense.is_cash = is_cash
        expense.expense_category_id = expense_category_id
        expense.credit_card_id = new_credit_card_id
        expense.bank_account_id = new_bank_account_id
        expense.description = description

        db.session.commit()

        CashLedger.update_or_delete(expense, delete_ledger=False)
        
        BankAccountTransactionsLedger.update(expense)
        
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
    try:
        if expense.credit_card or expense.bank_account:
            return_money(expense)
            BankAccountTransactionsLedger.delete(expense)

        CashLedger.update_or_delete(expense, delete_ledger=True)
        
        db.session.delete(expense)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception('Database error occurred: ' + str(e))
    except Exception as e:
        db.session.rollback()
        raise e 

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
        ).order_by(Expense.created_at.desc()).all()

        for e in expenses:
            data_from_database.append(e.to_dict())

    except Exception as e:
        print(e)
    
    return data_from_database

def filter_weekly_basis_expenses_info():
    start_date, end_date = get_current_week_range()
    end_date += timedelta(days=1)
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

def get_monthly_expenses_records():
    now = datetime.now()
    year = now.year
    month = now.month

    records = (
        Expense.query
        .filter(
            func.extract('year', Expense.created_at) == year,
            func.extract('month', Expense.created_at) == month
        )
        .order_by(Expense.created_at.desc())
        .all()
    )

    return records

def filter_expenses_by_is_cash(is_cash):
    data = {}

    try:
        expenses = Expense.query.filter(Expense.is_cash == is_cash).all()
        count = Expense.query.filter(Expense.is_cash == is_cash).count()
        total = Expense.query.filter(Expense.is_cash == is_cash).with_entities(func.sum(Expense.amount)).scalar() or Decimal(0.00)

        expenses_to_dict = []
        for e in expenses:
            expenses_to_dict.append(e.to_dict()) 
        data = {
            'expenses': expenses_to_dict,
            'count': count,
            'total': total,
        }
    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify(data)

def filter_by_field(query):
    try:
        is_cash = evaluate_boolean_columns(query, 'yes', 'no')    
        q = f'%{query}%'
        expenses_list = []

        filters = [
            CreditCard.nick_name.ilike(q),
            BankAccount.nick_name.ilike(q),
            ExpenseCategory.name.ilike(q),
            Expense.description.ilike(q),
            Expense.amount.ilike(q)
        ]

        if is_cash is not None:
            filters.append(Expense.is_cash == is_cash)

        expenses = (
            Expense.query
            .outerjoin(Expense.bank_account) #allows to show expense without a bank account
            .outerjoin(Expense.credit_card) #allows to show expense without a credit card
            .outerjoin(Expense.expense_category) #allows to show expense without an expense category
            .filter(or_(*filters))
            .order_by(Expense.created_at.desc())
            .all()
        )

        for expense in expenses:
            expenses_list.append(expense.to_dict())

        return jsonify({
            'expenses': expenses_list,
            'count': len(expenses_list),
            'total': total_amount(expenses)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        raise e

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

    limit = ExpenseCategory.query.filter(ExpenseCategory is not None).with_entities(func.sum(ExpenseCategory.limit)).scalar() or Decimal(0.00)
    
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

def update_bank_account_money_on_update(old_ba_id, new_ba_id, old_amount, new_amount):
    if (old_ba_id == new_ba_id) and (old_amount == new_amount): return

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
        traceback.print_exc()
        raise 
    
def update_credit_card_money_on_update(is_cash, old_cc_id, new_cc_id, old_amount, new_amount):
    if (old_cc_id == new_cc_id) and (new_amount == old_amount): return

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
        traceback.print_exc()
        raise 

def update_credit_card_or_bank_account_money_when_you_update_from_one_to_another(selected_bank_account, selected_credit_card, expense, old_amount, new_amount):
        bank_account = None
        credit_card = None
        bank_account_id = 0
        credit_card_id = 0

        '''
        The logic of this function is that an expense lets say it was made with a bank account, 
        obviously the credit card property of the expense object will have None as value.

        So in order to retrieve the money used from the bank account we access it through the expense object,
        on the other hand the credit card property will have None as value, so we'll have to take the id selected when
        the expense info was being edited in the frontend by a user.

        That way we query that credit card record using the selected id and then refund the money we took to the bank account
        and then take it from the credit card.

        Same process when an expense is changed from being made with a credit card to a bank account.
        '''
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
            traceback.print_exc()

def return_money(expense):

    if expense.bank_account:
        expense.bank_account.amount_available += expense.amount
    else:
        expense.credit_card.amount_available += expense.amount

def evaluate_boolean_columns(query, reference_for_true, reference_for_false):
    q = query.lower()
    if q == reference_for_true.lower():
        return True
    if q == reference_for_false.lower():
        return False
    return None
