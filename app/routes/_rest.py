"""Binds the URLs of a resource to its controller handlers (see app/controllers/_rest.py)."""
from flask_login import login_required

from app.controllers._rest import handlers


def register(blueprint, resource, prefix=''):
    """GET/POST `<prefix>`, GET/PUT/DELETE `<prefix>/<id>` of the blueprint, only the verbs the resource supports."""
    view = handlers(resource)
    name = (prefix.strip('/').replace('/', '_') or 'record').replace('-', '_')

    def add(rule, key, verb):
        blueprint.add_url_rule(rule, f'{name}_{key}', login_required(view[key]), methods=[verb])

    add(prefix or '', 'list', 'GET')
    if resource.create:
        add(prefix or '', 'create', 'POST')
    add(f'{prefix}/<int:record_id>', 'read', 'GET')
    if resource.update:
        add(f'{prefix}/<int:record_id>', 'update', 'PUT')
    if resource.delete:
        add(f'{prefix}/<int:record_id>', 'delete', 'DELETE')
