"""How a controller turns an HTTP request into a service call and the result into JSON.

A controller module declares a `Resource`: which schema validates the JSON body, which service function
does the work, how a record is serialized. The handlers below do the HTTP part for every resource the same way:

    GET    <prefix>          list (?q=text &start=YYYY-MM-DD &end=YYYY-MM-DD where the resource is searchable)
    POST   <prefix>          JSON body -> service.create   -> 201 {"data": record}
    GET    <prefix>/<id>     one record
    PUT    <prefix>/<id>     JSON body -> service.update   -> {"data": record}
    DELETE <prefix>/<id>     service.delete                -> 204

    success   {"data": ...}  and, for lists, {"data": [...], "meta": {"count": n, "total": "1.00", ...}}
    failure   {"error": {"code": "...", "message": "...", "fields": {...}}}   (see app/errors.py)

The routes (app/routes) only say which URL goes to which handler.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Callable, Optional

from flask import jsonify, request

from app.errors import error_response
from app.services import money
from app.utils.times import from_client

DATE_FORMAT = '%Y-%m-%d'


@dataclass
class Resource:
    label: str                                 # 'Expense'   (used in "Expense not found")
    model: type
    serialize: Callable
    create_schema: Optional[type] = None
    create: Optional[Callable] = None
    update_schema: Optional[type] = None       # same as create_schema when None
    update: Optional[Callable] = None
    delete: Optional[Callable] = None
    default_list: Optional[Callable] = None    # () -> records, when no filter is given
    filter: Optional[Callable] = None          # (query, start, end) -> records
    list_meta: Optional[Callable] = None       # (records) -> dict merged into meta
    stored_as_utc: bool = True                 # False for expenses and incomes (see app/utils/times.py)
    has_amount: bool = True


def json_body(schema, stored_as_utc=True):
    """Validate the JSON body of the request and return it as the keyword arguments of the service."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError('The request body must be a JSON object.')

    data = schema.model_validate(payload).model_dump()
    if 'created_at' in data:
        data['created_at'] = from_client(data['created_at'], stored_as_utc)
    return data


def _day(name):
    value = request.args.get(name)
    if not value:
        return None
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValueError(f'{name} must look like YYYY-MM-DD.')
    return value


def list_response(resource, records, extra_meta=None):
    meta = {'count': len(records)}
    if resource.has_amount:
        meta['total'] = f"{sum((r.amount for r in records), Decimal()):.2f}"
    if resource.list_meta:
        meta.update(resource.list_meta(records))
    if extra_meta:
        meta.update(extra_meta)
    return jsonify({'data': [resource.serialize(r) for r in records], 'meta': meta})


def data(payload, status=200):
    return jsonify({'data': payload}), status


def handlers(resource):
    """The five view functions of a resource, as a dict: list, create, read, update, delete."""

    def list_records():
        query, start, end = request.args.get('q'), _day('start'), _day('end')
        if bool(start) != bool(end):
            return error_response(422, 'validation_error', 'start and end go together.',
                                  {'start': 'Send both dates or none.'})

        if (query or (start and end)) and resource.filter:
            records = resource.filter(query=query, start=start, end=end)
        elif resource.default_list:
            records = resource.default_list()
        else:
            records = []
        return list_response(resource, records)

    def create_record():
        record = resource.create(**json_body(resource.create_schema, resource.stored_as_utc))
        return data(resource.serialize(record), 201)

    def read_record(record_id):
        return data(resource.serialize(money.get_record(resource.model, record_id, resource.label)))

    def update_record(record_id):
        schema = resource.update_schema or resource.create_schema
        record = resource.update(record_id, **json_body(schema, resource.stored_as_utc))
        return data(resource.serialize(record))

    def delete_record(record_id):
        resource.delete(record_id)
        return '', 204

    return {'list': list_records, 'create': create_record, 'read': read_record,
            'update': update_record, 'delete': delete_record}


def year_param():
    """`?year=2026` of the reports (None when missing: the service uses this year)."""
    value = request.args.get('year')
    if not value:
        return None
    try:
        year = int(value)
    except ValueError:
        raise ValueError('year must be a number.')
    if not 2000 <= year <= 2100:
        raise ValueError('year is out of range.')
    return year


def payments_resource(serialize):
    """A list-only Resource, to answer with the payments that hang from a loan or a debt."""
    return Resource(label='Payment', model=None, serialize=serialize)
