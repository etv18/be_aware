"""The React app is the only frontend: every page URL answers with the same index.html and React Router draws the page."""
import pytest

from app.routes import spa_routes


@pytest.fixture()
def built(tmp_path, monkeypatch):
    (tmp_path / 'index.html').write_text('<div id="root"></div>')
    monkeypatch.setattr(spa_routes, 'BUILD', tmp_path)


def test_every_page_url_gets_the_shell(app, built):
    anonymous = app.test_client()  # not logged in: the React app sends people to /login by itself

    for url in ['/', '/login', '/expenses', '/loans/12', '/bank_accounts/3', '/loan_payments']:
        response = anonymous.get(url)
        assert response.status_code == 200, url
        assert b'id="root"' in response.data
        assert response.headers['Cache-Control'] == 'no-cache'


def test_it_says_what_to_do_when_the_app_is_not_built(app, tmp_path, monkeypatch):
    monkeypatch.setattr(spa_routes, 'BUILD', tmp_path / 'missing')

    response = app.test_client().get('/expenses')

    assert response.status_code == 503
    assert b'npm run build' in response.data


def test_the_api_is_not_swallowed_by_the_shell(app, built):
    assert app.test_client().get('/api/expenses').status_code == 401


def test_a_wrong_api_or_file_url_is_a_404_not_the_app(client, built):
    for url in ['/api/nothing_here', '/static/missing.js']:
        assert client.get(url).status_code == 404, url
    assert client.get('/api/nothing_here').get_json()['error']['code'] == 'not_found'
