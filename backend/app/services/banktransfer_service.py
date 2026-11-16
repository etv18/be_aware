"""Business rules for bank transfers: money moves from one bank account to another.

Each transfer writes two ledger rows (one per account). No Flask in here; every write runs in
atomic() so the transfer, both balances and both ledger rows are saved together or not at all.
"""
from app.extensions import db
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.banktransfer import BankTransfer
from app.exceptions.bankProductsException import BankAccountDoesNotExists, NoAvailableMoney, SameBankAccountSelected
from app.models.bank_account import BankAccount
from app.services import money, search as search_service
from app.services.search import SearchSpec
from app.utils.date_handling import utcnow
from app.utils.transactions import atomic

SPEC = SearchSpec(
    model=BankTransfer,
    text_columns=(BankTransfer.amount, BankTransfer.code),
    extra_filter_columns=(BankTransfer.code,),
)


def create_banktransfer(*, amount, from_bank_account_id, to_bank_account_id, created_at=None):
    amount = money.validate_amount(amount)

    with atomic():
        origin = _get_account(from_bank_account_id, 'Origin')
        destination = _get_account(to_bank_account_id, 'Destination')
        _require_different(origin, destination)

        _require_funds(origin, amount, 'Origin bank account')
        origin.amount_available -= amount
        destination.amount_available += amount

        transfer = BankTransfer(
            amount=amount,
            from_bank_account_id=origin.id,
            to_bank_account_id=destination.id,
            created_at=created_at or utcnow(),
        )
        db.session.add(transfer)
        db.session.flush()

        BankAccountTransactionsLedger.create(transfer, commit=False)

    return transfer


def update_banktransfer(transfer_id, *, amount, to_bank_account_id, created_at=None):
    """Change the amount and/or the destination. The origin account of a transfer never changes."""
    amount = money.validate_amount(amount)

    with atomic():
        transfer = money.get_record(BankTransfer, transfer_id, 'Bank transfer')
        origin = transfer.from_bank_account
        old_destination = transfer.to_bank_account
        new_destination = _get_account(to_bank_account_id, 'Destination')
        _require_different(origin, new_destination)

        # undo the old transfer: the old destination hands the money back to the origin...
        _require_funds(old_destination, transfer.amount, old_destination.nick_name.capitalize())
        old_destination.amount_available -= transfer.amount
        origin.amount_available += transfer.amount

        # ...then do the new one
        _require_funds(origin, amount, origin.nick_name.capitalize())
        origin.amount_available -= amount
        new_destination.amount_available += amount

        transfer.amount = amount
        transfer.to_bank_account_id = new_destination.id
        if created_at:
            transfer.created_at = created_at

        db.session.flush()
        db.session.expire(transfer, ['to_bank_account'])

        BankAccountTransactionsLedger.update(transfer, commit=False)

    return transfer


def delete_banktransfer(transfer_id):
    with atomic():
        transfer = money.get_record(BankTransfer, transfer_id, 'Bank transfer')
        destination = transfer.to_bank_account

        _require_funds(destination, transfer.amount, destination.nick_name.capitalize())
        destination.amount_available -= transfer.amount
        transfer.from_bank_account.amount_available += transfer.amount

        BankAccountTransactionsLedger.delete(transfer, commit=False)
        db.session.delete(transfer)


def list_all():
    return BankTransfer.query.order_by(BankTransfer.created_at.desc()).all()


def filter_transfers(query=None, start=None, end=None):
    return search_service.filter_all(SPEC, query, start, end)


def get_transfer(transfer_id):
    return money.get_record(BankTransfer, transfer_id, 'Bank transfer')


# ------------------------------------------------------------------ helpers

def _get_account(account_id, role):
    try:
        return money.get_bank_account(account_id)
    except BankAccountDoesNotExists:
        raise BankAccountDoesNotExists(f'{role} bank account was not found.')


def _require_different(origin, destination):
    if origin.id == destination.id:
        raise SameBankAccountSelected('You can not select the same account.')


def _require_funds(account, amount, name):
    if account.amount_available <= 0 or account.amount_available < amount:
        raise NoAvailableMoney(f'{name} does not have enough founds.')
