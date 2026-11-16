"""One implementation of the list / search / date-range filters every records page has.

Each module describes itself with a SearchSpec and gets the same three queries:
    between_dates  -> the "from / to" date pickers
    search         -> the search box (free text)
    filter_all     -> search box and date pickers combined

Typing one of the module's keywords exactly ("yes" / "no" for is-cash, "active" / "paid" for loans) filters on
that boolean column instead of searching text.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, or_

DATE_FORMAT = '%Y-%m-%d'


@dataclass(frozen=True)
class SearchSpec:
    model: type
    # relationships to outer join, so records without a bank account / card / category are still listed
    joins: tuple = ()
    # columns the search box looks into
    text_columns: tuple = ()
    # extra columns only the combined filter looks into (the record code, usually)
    extra_filter_columns: tuple = ()
    # (column, column): in the combined filter "first, second" narrows by both ("Checking, income" on the
    # bank ledger means account name AND transaction type)
    pair_columns: tuple = ()
    # words that filter on a boolean column when typed exactly, as (word for True, word for False, column):
    # ('yes', 'no', Income.is_cash) or ('active', 'paid', Loan.is_active)
    keywords: tuple = ()
    order_by: object = None

    def ordering(self):
        return self.order_by if self.order_by is not None else self.model.created_at.desc()


def parse_keyword(text, true_word, false_word):
    """true_word -> True, false_word -> False, anything else -> None (case insensitive)."""
    text = (text or '').lower()
    if text == true_word.lower():
        return True
    if text == false_word.lower():
        return False
    return None


def parse_day(text):
    return datetime.strptime(text, DATE_FORMAT)


def _base_query(spec):
    query = spec.model.query
    for relationship in spec.joins:
        query = query.outerjoin(relationship)
    return query


def _like_any(columns, text):
    pattern = f'%{text}%'
    return or_(*[column.ilike(pattern) for column in columns])


def _text_condition(spec, text, columns):
    """The condition for one piece of search text: a keyword's boolean column, or a text match."""
    for true_word, false_word, column in spec.keywords:
        flag = parse_keyword(text, true_word, false_word)
        if flag is not None:
            return column == flag
    return _like_any(columns, text)


def _query_condition(spec, query):
    """The condition for the search box text of the combined filter."""
    columns = spec.text_columns + spec.extra_filter_columns

    if spec.pair_columns and ',' in query:
        terms = [term.strip() for term in query.split(',') if term.strip()]
        if len(terms) == 1:
            return _like_any(columns, terms[0])
        if len(terms) == 2:
            first, second = spec.pair_columns
            return and_(first.ilike(f'%{terms[0]}%'), second.ilike(f'%{terms[1]}%'))
        return None  # more than two terms: nothing to narrow by

    return _text_condition(spec, query, columns)


def between_dates(spec, start, end):
    """Records from `start` up to the end of `end` (datetime or 'YYYY-MM-DD' strings)."""
    start = parse_day(start) if isinstance(start, str) else start
    end = parse_day(end) if isinstance(end, str) else end

    return (
        spec.model.query
        .filter(spec.model.created_at.between(start, end + timedelta(days=1)))
        .order_by(spec.ordering())
        .all()
    )


def search(spec, text):
    text = text or ''
    condition = _text_condition(spec, text, spec.text_columns)
    return _base_query(spec).filter(condition).order_by(spec.ordering()).all()


def filter_all(spec, query=None, start=None, end=None):
    conditions = []

    if start and end:
        conditions.append(spec.model.created_at.between(parse_day(start), parse_day(end) + timedelta(days=1)))

    if query:
        condition = _query_condition(spec, query)
        if condition is not None:
            conditions.append(condition)

    return _base_query(spec).filter(and_(*conditions)).order_by(spec.ordering()).all()


def sum_amount(records):
    return sum((r.amount for r in records), Decimal())
