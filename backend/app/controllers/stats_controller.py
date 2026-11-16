"""Charts and totals. Read only; `?year=` picks the year (this year when missing)."""
from flask import request

from app.controllers._rest import data, year_param
from app.services import stats_service


def yearly_report():
    """One kind of record: ?model=expenses|incomes|withdrawals|deposits|loans|debts|... """
    model = request.args.get('model')
    report = stats_service.yearly_single_model(model, year_param())
    if not report:
        raise ValueError(f'Unknown model "{model}".')
    return data(report)


def yearly_all_report():
    return data(stats_service.yearly_all_models(year_param()))


def incomings_and_outgoings():
    return data(stats_service.yearly_incomes_and_outgoings(year_param()))


def incomings_and_outgoings_monthly():
    return data(stats_service.monthly_incomings_and_outgoings())


def cash_flow_report():
    return data(stats_service.cash_flow(year_param()))


def bank_accounts_by_source():
    return data(stats_service.bank_account_yearly_by_source(year_param()))


def credit_cards_by_source():
    return data(stats_service.credit_card_yearly_by_source(year_param()))


def cash_by_source():
    return data(stats_service.cash_yearly_by_source(year_param()))
