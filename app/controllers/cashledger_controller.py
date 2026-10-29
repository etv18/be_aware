"""The three ledgers (read only: the money services write them) and the cash adjustments."""
from app.controllers import schemas, serializers as ser
from app.controllers._rest import Resource, data, json_body
from app.controllers.serializers import money
from app.models.bank_account_transactions_ledger import BankAccountTransactionsLedger
from app.models.cash_ledger import CashLedger
from app.models.credit_card_transactions_ledger import CreditCardTransactionsLedger
from app.services import ledger_service


def _ledger(label, model, serialize, spec, default_list, list_meta=None, create=None, create_schema=None):
    return Resource(
        label=label, model=model, serialize=serialize, create_schema=create_schema, create=create,
        default_list=default_list,
        filter=lambda query=None, start=None, end=None: ledger_service.filter_ledger(spec, query, start, end),
        list_meta=list_meta,
    )


# POST /cashledger is a manual adjustment; there is no PUT, and DELETE only works on adjustments
CASH = _ledger('Cash ledger entry', CashLedger, ser.cash_ledger, ledger_service.CASH_SPEC, ledger_service.list_cash,
               lambda records: {'balance': money(ledger_service.cash_balance())},
               create=ledger_service.create_cash_adjustment, create_schema=schemas.CashAdjustmentIn)
CASH.delete = ledger_service.delete_cash_adjustment

BANK = _ledger('Ledger entry', BankAccountTransactionsLedger, ser.bank_ledger, ledger_service.BANK_SPEC,
               ledger_service.list_bank)
CARD = _ledger('Ledger entry', CreditCardTransactionsLedger, ser.card_ledger, ledger_service.CARD_SPEC,
               ledger_service.list_card)
