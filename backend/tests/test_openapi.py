"""The OpenAPI document: valid, complete, and the same thing the API really answers."""
import json
import re

import jsonschema
import pytest
from openapi_spec_validator import validate

from app.openapi import build_spec

# Endpoints whose answer is not described by a model yet. The list only gets shorter: describe one in
# app/controllers/out.py, pass `out=` to get() in its routes file, and delete it here.
NOT_TYPED_YET = {
    '/api/bank_accounts/{account_id}/records',
    '/api/bank_accounts/{account_id}/reports/cash_flow',
    '/api/bank_accounts/{account_id}/reports/monthly',
    '/api/bank_accounts/{account_id}/reports/yearly',
    '/api/credit_cards/{card_id}/records',
    '/api/credit_cards/{card_id}/reports/yearly',
    '/api/expense_categories/{category_id}/records',
    '/api/expense_categories/reports/monthly',
    '/api/reports/cash_flow',
    '/api/reports/incomings_and_outgoings',
    '/api/reports/incomings_and_outgoings/monthly',
    '/api/reports/sources/bank_accounts',
    '/api/reports/sources/cash',
    '/api/reports/sources/credit_cards',
    '/api/reports/yearly/all',
}


@pytest.fixture()
def spec(app):
    return build_spec(app)


def operations(spec):
    for path, methods in spec['paths'].items():
        for method, operation in methods.items():
            yield path, method, operation


def test_the_document_is_valid_openapi(spec):
    validate(spec)


def test_every_api_route_is_in_the_document(app, spec):
    wanted = {
        (rule.rule.replace('<int:', '{').replace('>', '}'), method.lower())
        for rule in app.url_map.iter_rules() if rule.rule.startswith('/api/') and not rule.endpoint.startswith('openapi.')
        for method in rule.methods - {'HEAD', 'OPTIONS'}
    }
    documented = {(path, method) for path, method, _ in operations(spec)}

    assert wanted == documented


def test_only_the_known_endpoints_are_not_typed_yet(spec):
    untyped = {path for path, _, op in operations(spec) if op.get('x-typed') is False}

    assert untyped == NOT_TYPED_YET


def test_every_reference_resolves(spec):
    names = set(spec['components']['schemas'])
    references = set(re.findall(r'#/components/schemas/(\w+)', json.dumps(spec)))

    assert references <= names


def test_a_real_list_answer_fits_the_document(client, data, spec):
    client.post('/api/expenses', json={
        'amount': '12.50', 'is_cash': True, 'description': 'Lunch', 'expense_category_id': data['food'].id,
    })
    body = client.get('/api/expenses', query_string={'q': 'Lunch'}).get_json()

    schema = spec['paths']['/api/expenses']['get']['responses']['200']['content']['application/json']['schema']
    document = {'components': spec['components'], **schema}
    jsonschema.validate(body, document)


def test_the_docs_are_served_in_development_and_tests(client):
    assert client.get('/api/openapi.json').get_json()['openapi'] == '3.1.0'
    assert client.get('/api/docs').status_code == 200


def test_the_docs_are_only_turned_on_for_development_and_tests():
    from app.config import get_config

    assert get_config('development').OPENAPI_ENABLED is True
    assert get_config('testing').OPENAPI_ENABLED is True
    assert get_config('production').OPENAPI_ENABLED is False


@pytest.mark.parametrize('path', ['/api/options', '/api/dashboard', '/api/session'])
def test_the_other_answers_fit_the_document_too(client, spec, path):
    body = client.get(path).get_json()

    schema = spec['paths'][path]['get']['responses']['200']['content']['application/json']['schema']
    jsonschema.validate(body, {'components': spec['components'], **schema})


def test_the_session_tells_the_page_which_environment_it_runs_in(client):
    session = client.get('/api/session').get_json()['data']

    assert session['authenticated'] is True
    assert (session['env_name'], session['env_label']) == ('testing', 'TEST')


def test_the_exported_file_is_up_to_date(spec):
    """frontend/openapi.json (and the TypeScript types made from it) must be regenerated when the API changes."""
    from pathlib import Path

    exported = json.loads((Path(__file__).resolve().parent.parent.parent / 'frontend' / 'openapi.json').read_text(encoding='utf-8'))

    assert exported == json.loads(json.dumps(spec)), 'The API changed: run "npm run gen:api" in /frontend and commit the result.'
