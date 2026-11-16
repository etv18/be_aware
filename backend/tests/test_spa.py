"""The React app is served under /app: any URL there answers with the same index.html."""
import pytest

from app.routes import spa_routes


@pytest.fixture()
def built(tmp_path, monkeypatch):
    (tmp_path / 'index.html').write_text('<div id="root"></div>')
    monkeypatch.setattr(spa_routes, 'BUILD', tmp_path)


def test_every_url_below_app_gets_the_shell(app, built):
    anonymous = app.test_client()

    for url in ['/app', '/app/', '/app/login', '/app/expenses', '/app/loans/12']:
        response = anonymous.get(url)
        assert response.status_code == 200, url
        assert b'id="root"' in response.data
        assert response.headers['Cache-Control'] == 'no-cache'


def test_it_says_what_to_do_when_the_app_is_not_built(app, tmp_path, monkeypatch):
    monkeypatch.setattr(spa_routes, 'BUILD', tmp_path / 'missing')

    response = app.test_client().get('/app/expenses')

    assert response.status_code == 503
    assert b'npm run build' in response.data


def test_the_api_is_not_swallowed_by_the_shell(app, built):
    assert app.test_client().get('/api/expenses').status_code == 401
