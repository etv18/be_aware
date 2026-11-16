"""Security of the JSON API and the environment badge. (The pages themselves are the React app: see test_spa.py.)"""


def test_api_rejects_unsafe_requests_without_a_csrf_token(app, data):
    app.config['WTF_CSRF_ENABLED'] = True
    client = app.test_client()
    with client.session_transaction() as s:
        s['_user_id'] = str(data['user'].id)

    body = {'amount': '10', 'is_cash': True, 'expense_category_id': data['food'].id, 'description': 'x'}
    refused = client.post('/api/expenses', json=body)
    assert refused.status_code == 400 and refused.get_json()['error']['code'] == 'csrf_failed'

    token = client.get('/api/session').get_json()['data']['csrf_token']
    accepted = client.post('/api/expenses', json=body, headers={'X-CSRFToken': token})
    assert accepted.status_code == 201, accepted.get_json()


def test_each_environment_has_its_own_badge():
    from app.config import get_config

    assert get_config('development').ENV_LABEL == 'DEV'
    assert get_config('testing').ENV_LABEL == 'TEST'
    assert get_config('production').ENV_LABEL == 'PROD'
