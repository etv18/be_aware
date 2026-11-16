"""Binds URLs to controller handlers.

Pages live at plain URLs (/expenses, /loans/12). The JSON of the same things lives under /api
(/api/expenses, /api/loans/12), written in snake_case and plural: /api/<resource> and /api/<resource>/<id>.
"""
from flask_login import login_required

from app.controllers._rest import handlers
from app.openapi import document

API = '/api'


def register(blueprint, resource, path):
    """The JSON of one resource: GET/POST /api<path>, GET/PUT/DELETE /api<path>/<id> (only the verbs it supports)."""
    view = handlers(resource)

    def add(rule, key, verb):
        blueprint.add_url_rule(f'{API}{rule}', f'record_{key}', login_required(view[key]), methods=[verb])
        document(f'{blueprint.name}.record_{key}', kind=key, resource=resource)  # for the OpenAPI document

    add(path, 'list', 'GET')
    if resource.create:
        add(path, 'create', 'POST')
    add(f'{path}/<int:record_id>', 'read', 'GET')
    if resource.update:
        add(f'{path}/<int:record_id>', 'update', 'PUT')
    if resource.delete:
        add(f'{path}/<int:record_id>', 'delete', 'DELETE')


def get(blueprint, path, view, name, out=None, many=False, query=(), summary=None):
    """A read-only JSON endpoint: GET /api<path>.

    For the OpenAPI document: `out` is the model of "data" (many=True when it is a list of them) and `query` the
    names of the query parameters it reads. Without `out` the endpoint is listed as "not typed yet".
    """
    blueprint.add_url_rule(f'{API}{path}', name, login_required(view), methods=['GET'])
    document(f'{blueprint.name}.{name}', out=out, many=many, query=query, summary=summary)
