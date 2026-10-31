from flask import Flask, render_template
from flask_migrate import Migrate
from flask_babel import format_datetime, format_date, format_time
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.engine import make_url

import os
import logging
from logging.handlers import RotatingFileHandler

from app.config import get_config
from app.cli import register_cli
from app.utils.date_handling import format_datetime_filter
from app.errors import register_error_handlers, unauthorized
from app.extensions import db, babel, limiter, crsf, login_manager
from app.routes import (
    home_routes, 
    bank_routes, 
    bank_account_routes, 
    credit_card_routes, 
    expense_category_routes, 
    expense_routes, 
    income_routes, 
    loan_routes,
    loan_payment_routes,
    credit_card_payment_routes, 
    withdrawal_routes, 
    cashledger_routes,
    banktransfer_routes,
    bank_transaction_ledger_routes,
    debt_routes,
    debt_payment_routes,
    deposit_routes,
    credit_card_transaction_routes,
    stats_routes,
    auth_routes,
)

def create_app(config_name=None):
    """Application factory. `config_name` is 'development', 'testing' or 'production';
    when omitted it comes from the APP_ENV variable (default: development)."""
    config = get_config(config_name)

    app = Flask(__name__)
    app.config.from_object(config)

    # SQLite files for development live in the instance folder
    os.makedirs(app.instance_path, exist_ok=True)

    # Fix real IP (VERY IMPORTANT with Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    register_extensions(app)
    register_resources(app)
    register_cli(app)

    create_error_logger(app)

    # Only the backend name is logged, never the connection string (it holds credentials)
    app.logger.info(
        'Be Aware started with %s using the %s database',
        type(config).__name__,
        make_url(app.config['SQLALCHEMY_DATABASE_URI']).get_backend_name(),
    )

    @app.context_processor
    def inject_theme():
        return {
            'nav_bar_backgroud': app.config['NAV_BAR_BACKGROUND_COLOR'],
            # the badge in the navbar: APP_ENV of the .env file -> DEV / PROD / TEST
            'env_name': app.config['ENV_NAME'],
            'env_label': app.config['ENV_LABEL'],
        }

    from app import models

    return app

def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    babel.init_app(app)
    limiter.init_app(app)
    crsf.init_app(app)
    login_manager.init_app(app)

    #LOGIN MANAGER
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    login_manager.unauthorized_handler(unauthorized)
    register_error_handlers(app)

    #GLOBAL rate limiter
    limiter.default_limits = ['600 per minute']  # a page makes several calls per screen

    # REGISTER BABEL FILTERS MANUALLY (Flask-Babel 4.x)
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_time'] = format_time

    # Register custom the filter with Jinja
    app.jinja_env.filters['format_datetime_custom'] = format_datetime_filter

def register_resources(app):
    app.register_blueprint(home_routes.home_bp)
    app.register_blueprint(bank_routes.bank_bp)
    app.register_blueprint(bank_account_routes.bank_account_bp)
    app.register_blueprint(credit_card_routes.credit_card_bp)
    app.register_blueprint(expense_category_routes.expense_category_bp)
    app.register_blueprint(expense_routes.expense_bp)
    app.register_blueprint(income_routes.income_bp)
    app.register_blueprint(loan_routes.loan_bp)
    app.register_blueprint(loan_payment_routes.loan_payment_bp)
    app.register_blueprint(credit_card_payment_routes.credit_card_payment_bp)
    app.register_blueprint(withdrawal_routes.withdrawal_bp)
    app.register_blueprint(cashledger_routes.cash_ledger_bp)
    app.register_blueprint(banktransfer_routes.banktransfer_bp)
    app.register_blueprint(bank_transaction_ledger_routes.bank_transaction_ledger_bp)
    app.register_blueprint(debt_routes.debt_bp)
    app.register_blueprint(debt_payment_routes.debt_payment_bp)
    app.register_blueprint(deposit_routes.deposit_bp)
    app.register_blueprint(credit_card_transaction_routes.credit_card_ledger_bp)
    app.register_blueprint(stats_routes.stats_bp)
    app.register_blueprint(auth_routes.auth)

def create_error_logger(app):
    # Tests (and anything else that sets LOG_TO_FILES = False) skip the log files
    if not app.config.get('LOG_TO_FILES', True):
        return

    if not os.path.exists('logs'):
        os.makedirs('logs')

    formatter = logging.Formatter(
        "\n\n" +
        "=" * 156 + "\n"
        "%(asctime)s | %(levelname)s\n"
        "Message: %(message)s\n"
        "File: %(pathname)s:%(lineno)d\n"
        + "=" * 156 + ""
    )

    # Remove default handlers
    app.logger.handlers.clear()

    # ERROR FILE
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10240,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # GENERAL FILE
    info_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,
        backupCount=10
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    app.logger.addHandler(error_handler)
    app.logger.addHandler(info_handler)

