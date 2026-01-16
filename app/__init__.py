from flask import Flask
from flask_migrate import Migrate

import os
import logging
from logging.handlers import RotatingFileHandler

from app.config import Config
from app.extensions import db
from app.routes import (
    home_routes, 
    bank_routes, 
    bank_account_routes, 
    credit_card_routes, 
    expense_category_routes, 
    expense_routes, 
    income_routes, 
    accounts_receivable_routes, 
    credit_card_payment_routes, 
    withdrawal_routes, 
    cashledger_routes,
    banktransfer_routes,
    bank_transaction_ledger_routes,
    debt_routes,
    debt_payment_routes,
    deposit_routes,
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_resources(app)

    create_error_logger(app)

    from app import models

    return app

def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)

def register_resources(app):
    app.register_blueprint(home_routes.home_bp)
    app.register_blueprint(bank_routes.bank_bp)
    app.register_blueprint(bank_account_routes.bank_account_bp)
    app.register_blueprint(credit_card_routes.credit_card_bp)
    app.register_blueprint(expense_category_routes.expense_category_bp)
    app.register_blueprint(expense_routes.expense_bp)
    app.register_blueprint(income_routes.income_bp)
    app.register_blueprint(accounts_receivable_routes.accounts_receivable_bp)
    app.register_blueprint(credit_card_payment_routes.credit_card_payment_bp)
    app.register_blueprint(withdrawal_routes.withdrawal_bp)
    app.register_blueprint(cashledger_routes.cashlegder_bp)
    app.register_blueprint(banktransfer_routes.banktransfer_bp)
    app.register_blueprint(bank_transaction_ledger_routes.bank_transaction_ledger_bp)
    app.register_blueprint(debt_routes.debt_bp)
    app.register_blueprint(debt_payment_routes.debt_payment_bp)
    app.register_blueprint(deposit_routes.deposit_bp)
    
def create_error_logger(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_file = os.path.join('logs', 'error.log')
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10240, #The file will store data up 10KB
        backupCount=10 #There will be a maximum of 10 backup files of errors
    )

    formatter = logging.Formatter(
        "\n\n"
        "=======================================================================================\n"
        "%(asctime)s [%(levelname)s] %(message)s in %(pathname)s:%(lineno)d\n"
    )

    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.ERROR)