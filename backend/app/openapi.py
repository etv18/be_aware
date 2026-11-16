"""The OpenAPI document of the JSON API, built from what the code already says.

Nothing is written by hand per endpoint:
  * the routes (app/routes/_rest.py) record what an endpoint takes and returns when they register
  * request bodies are the Pydantic schemas of app/controllers/schemas.py
  * responses are the models of app/controllers/out.py
  * the list of URLs comes from Flask itself, so a route added without being described still shows up
    (with a generic answer, marked `x-typed: false`) and tests/test_openapi.py lists it.

Served at /api/openapi.json, with a Swagger UI at /api/docs, while OPENAPI_ENABLED is on (development and tests).
`flask export-openapi` writes the same document to a file: the frontend generates its TypeScript types from it.
"""
import re
from dataclasses import dataclass
from typing import Optional

from flask import Blueprint, current_app, jsonify
from pydantic.json_schema import models_json_schema

from app.controllers import out as outs

REF = '#/components/schemas/{model}'
openapi_bp = Blueprint('openapi', __name__)


@dataclass
class Doc:
    """What a route tells the builder about one endpoint. DOCS is keyed by Flask endpoint name ('expense.record_list')."""
    kind: str                        # list | create | read | update | delete (REST, from a Resource) or custom
    resource: object = None          # REST kinds: the controllers._rest.Resource
    out: Optional[type] = None       # custom: the model of "data" (None: not described yet)
    many: bool = False               # custom: "data" is a list of `out`
    body: Optional[type] = None      # custom: the Pydantic model of the JSON body
    query: tuple = ()                # custom: names of query parameters (see QUERY)
    summary: Optional[str] = None
    no_content: bool = False         # custom: answers 204 with no body
    public: bool = False             # custom: works without being logged in


DOCS: dict = {}


def document(endpoint, kind='custom', **fields):
    DOCS[endpoint] = Doc(kind=kind, **fields)


QUERY = {
    'q': {'description': 'Text to look for (description, person, code or amount).', 'schema': {'type': 'string'}},
    'start': {'description': 'First day, YYYY-MM-DD. Send it together with `end`.', 'schema': {'type': 'string', 'format': 'date'}},
    'end': {'description': 'Last day, YYYY-MM-DD. Send it together with `start`.', 'schema': {'type': 'string', 'format': 'date'}},
    'year': {'description': 'Year of the report (this year when missing).', 'schema': {'type': 'integer'}},
    'model': {'description': 'Which kind of record: expenses, incomes, withdrawals, deposits, loans, debts, ...', 'schema': {'type': 'string'}},
}

ERROR_SCHEMA = {
    'type': 'object',
    'required': ['error'],
    'properties': {'error': {
        'type': 'object',
        'required': ['code', 'message'],
        'properties': {
            'code': {'type': 'string', 'description': 'Stable, for programs: validation_error, not_found, ...'},
            'message': {'type': 'string', 'description': 'For people.'},
            'fields': {'type': 'object', 'additionalProperties': {'type': 'string'}, 'description': 'Message per invalid field (422).'},
        },
    }},
}

ERRORS = {
    '400': 'A business rule refused the request (for example not enough money). `code` names the rule.',
    '401': 'Not logged in.',
    '404': 'The record does not exist.',
    '422': 'The body or the query is invalid. `fields` says which values.',
}


# ------------------------------------------------------------------ small helpers

def _ref(model):
    return {'$ref': REF.format(model=model.__name__)}


def _envelope(data, meta=None):
    properties, required = {'data': data}, ['data']
    if meta:
        properties['meta'] = meta
        required.append('meta')
    return {'type': 'object', 'required': required, 'properties': properties}


def _json(description, schema):
    return {'description': description, 'content': {'application/json': {'schema': schema}}}


def _path(rule):
    """'/api/expenses/<int:record_id>' -> '/api/expenses/{record_id}'"""
    return re.sub(r'<(?:\w+:)?(\w+)>', r'{\1}', rule.rule)


def _path_params(rule):
    return [{'name': name, 'in': 'path', 'required': True, 'schema': {'type': 'integer' if kind == 'int' else 'string'}}
            for kind, name in re.findall(r'<(?:(\w+):)?(\w+)>', rule.rule)]


def _query(name):
    return {'name': name, 'in': 'query', 'required': False, **QUERY[name]}


def _tag(path):
    return path.strip('/').split('/')[1]


def _plural(noun):
    return noun[:-1] + 'ies' if noun.endswith('y') else noun + 's'


def _words(rule):
    return rule.endpoint.split('.')[-1].replace('_', ' ')


# ------------------------------------------------------------------ one operation

def _operation(rule, method, doc, models):
    path = _path(rule)
    op = {'operationId': f"{rule.endpoint.replace('.', '_')}_{method}", 'tags': [_tag(path)]}
    params, responses, body = _path_params(rule), {}, None
    typed = doc is not None

    if doc is None:
        op['summary'] = _words(rule)
        responses['200'] = _json('The answer. Its shape is not described yet.', _envelope({'type': 'object'}))

    elif doc.kind != 'custom':
        resource = doc.resource
        noun = resource.label.lower()
        item = {'type': 'object'}
        if resource.out:
            models.append((resource.out, 'serialization'))
            item = _ref(resource.out)
        typed = resource.out is not None

        if doc.kind == 'list':
            op['summary'] = f'List {_plural(noun)}'
            if resource.filter:
                params += [_query(name) for name in ('q', 'start', 'end')]
            models.append((resource.meta_out, 'serialization'))
            responses['200'] = _json('The records.', _envelope({'type': 'array', 'items': item}, _ref(resource.meta_out)))
        elif doc.kind == 'read':
            op['summary'] = f'Read {noun}'
            responses['200'] = _json('The record.', _envelope(item))
        elif doc.kind == 'delete':
            op['summary'] = f'Delete {noun}'
            responses['204'] = {'description': 'Deleted. No body.'}
        else:
            create = doc.kind == 'create'
            schema = resource.create_schema if create else (resource.update_schema or resource.create_schema)
            models.append((schema, 'validation'))
            body = {'required': True, 'content': {'application/json': {'schema': _ref(schema)}}}
            op['summary'] = f"{'Create' if create else 'Update'} {noun}"
            responses['201' if create else '200'] = _json('The saved record.', _envelope(item))

    else:
        op['summary'] = doc.summary or _words(rule)
        params += [_query(name) for name in doc.query]
        if doc.body:
            models.append((doc.body, 'validation'))
            body = {'required': True, 'content': {'application/json': {'schema': _ref(doc.body)}}}
        if doc.no_content:
            responses['204'] = {'description': 'Done. No body.'}
        elif doc.out:
            models.append((doc.out, 'serialization'))
            data = _ref(doc.out)
            if doc.many:
                models.append((outs.ListMeta, 'serialization'))
                responses['200'] = _json('The answer.', _envelope({'type': 'array', 'items': data}, _ref(outs.ListMeta)))
            else:
                responses['200'] = _json('The answer.', _envelope(data))
        else:
            typed = False
            responses['200'] = _json('The answer. Its shape is not described yet.', _envelope({'type': 'object'}))

    public = doc is not None and doc.public
    changes = method in ('post', 'put', 'delete')
    if public:
        op['security'] = []
    elif changes:
        op['security'] = [{'cookieAuth': [], 'csrfToken': []}]
    else:
        op['security'] = [{'cookieAuth': []}]

    checks_input = body is not None or any(p['name'] == 'start' for p in params)
    errors = (['400'] if changes else []) + ([] if public else ['401']) + (['422'] if checks_input else [])
    errors += ['404'] if any(p['in'] == 'path' for p in params) else []
    for code in errors:
        responses[code] = {'$ref': f'#/components/responses/Error{code}'}

    if not typed:
        op['x-typed'] = False
    if params:
        op['parameters'] = params
    if body:
        op['requestBody'] = body
    op['responses'] = dict(sorted(responses.items()))
    return op


# ------------------------------------------------------------------ the whole document

def build_spec(app=None):
    """The OpenAPI 3.1 document as a dict."""
    app = app or current_app
    paths, models = {}, []

    rules = [r for r in app.url_map.iter_rules() if r.rule.startswith('/api/') and not r.endpoint.startswith('openapi.')]
    for rule in sorted(rules, key=lambda r: r.rule):
        for method in sorted(rule.methods - {'HEAD', 'OPTIONS'}):
            paths.setdefault(_path(rule), {})[method.lower()] = _operation(rule, method.lower(), DOCS.get(rule.endpoint), models)

    _, defs = models_json_schema(list(dict.fromkeys(models)), ref_template=REF)
    schemas_ = {**dict(sorted(defs.get('$defs', {}).items())), 'ErrorResponse': ERROR_SCHEMA}

    return {
        'openapi': '3.1.0',
        'info': {
            'title': 'Be Aware API',
            'version': '1.0.0',
            'description': (
                'JSON API of the Be Aware personal finance tracker.\n\n'
                'Success: `{"data": ...}` (lists also have `meta`). Failure: `{"error": {"code", "message", "fields"?}}`.\n\n'
                'Money is always a string with two decimals. The session is a cookie; send the CSRF token from '
                '`GET /api/session` in an `X-CSRFToken` header on POST, PUT and DELETE.'
            ),
        },
        'tags': [{'name': name} for name in sorted({_tag(path) for path in paths})],
        'paths': paths,
        'components': {
            'schemas': schemas_,
            'responses': {f'Error{code}': _json(text, {'$ref': '#/components/schemas/ErrorResponse'}) for code, text in ERRORS.items()},
            'securitySchemes': {
                'cookieAuth': {'type': 'apiKey', 'in': 'cookie', 'name': 'session', 'description': 'Set by POST /api/login.'},
                'csrfToken': {'type': 'apiKey', 'in': 'header', 'name': 'X-CSRFToken', 'description': 'The token of GET /api/session.'},
            },
        },
    }


def write_spec(path, app=None):
    """Save the document as JSON (sorted keys and LF line ends, so it only changes in git when the API does)."""
    import json

    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(build_spec(app), handle, indent=2, sort_keys=True)
        handle.write('\n')


# ------------------------------------------------------------------ serving it

@openapi_bp.get('/api/openapi.json')
def spec():
    return jsonify(build_spec())


@openapi_bp.get('/api/docs')
def docs():
    return (
        '<!doctype html><html><head><meta charset="utf-8"><title>Be Aware API</title>'
        '<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"></head>'
        '<body><div id="ui"></div>'
        '<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>'
        '<script>SwaggerUIBundle({url: "/api/openapi.json", dom_id: "#ui", persistAuthorization: true});</script>'
        '</body></html>'
    )


def register_openapi(app):
    """Serve /api/openapi.json and /api/docs when OPENAPI_ENABLED (development and tests, never production)."""
    if app.config.get('OPENAPI_ENABLED'):
        app.register_blueprint(openapi_bp)
