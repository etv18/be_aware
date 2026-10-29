from decimal import Decimal

import bcrypt
import click

from app.extensions import db


def register_cli(app):
    """Adds the `flask init-db` and `flask seed-db` commands used with the SQLite development database."""

    @app.cli.command('init-db')
    def init_db():
        """Create every table (safe to run again, existing tables are left alone)."""
        import app.models  # noqa: F401  makes sure every model is registered before create_all

        db.create_all()
        click.echo('Database tables created.')

    @app.cli.command('seed-db')
    @click.option('--username', default='admin', show_default=True)
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    def seed_db(username, password):
        """Create the tables plus a login user and a few demo records to try the app with."""
        import app.models  # noqa: F401
        from app.models.user import User
        from app.models.bank import Bank
        from app.models.bank_account import BankAccount
        from app.models.credit_card import CreditCard
        from app.models.expense_category import ExpenseCategory

        db.create_all()

        if User.query.filter_by(username=username).first():
            click.echo(f"User '{username}' already exists, nothing seeded.")
            return

        bank = Bank(name='Demo Bank')
        db.session.add(bank)
        db.session.flush()

        db.session.add_all([
            User(username=username, password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())),
            BankAccount(nick_name='Demo checking', amount_available=Decimal('1000.00'), bank_id=bank.id),
            CreditCard(nick_name='Demo card', amount_available=Decimal('500.00'), limit=Decimal('500.00'), bank_id=bank.id),
            ExpenseCategory(name='FOOD', limit=Decimal('300.00')),
            ExpenseCategory(name='TRANSPORT', limit=Decimal('100.00')),
        ])
        db.session.commit()

        click.echo(f"Seeded demo data. Log in as '{username}'.")
