"""The React app (built from /frontend into backend/app/static/app).

Every URL that is not the API and not a static file answers with the same index.html, and React Router draws the page
(/expenses, /loans/3, /login ...). The app is not behind login_required on purpose: its own RequireAuth sends anyone
who is not logged in to /login, and the data only comes from /api, which is.
"""
from pathlib import Path

from flask import Blueprint, abort, send_file

spa_bp = Blueprint('spa', __name__)

BUILD = Path(__file__).resolve().parent.parent / 'static' / 'app'


@spa_bp.get('/', defaults={'path': ''})
@spa_bp.get('/<path:path>')
def shell(path):
    if path.startswith(('api/', 'static/')):  # a wrong API or file URL is a 404, not the app
        abort(404)

    index = BUILD / 'index.html'
    if not index.exists():
        return 'The React app is not built yet. Run "npm run build" in the frontend folder.', 503

    response = send_file(index)
    response.headers['Cache-Control'] = 'no-cache'  # its script and style names change with every build
    return response
