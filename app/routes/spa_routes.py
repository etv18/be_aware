"""The React app (built from /frontend into app/static/app).

While the Jinja pages still exist the React app lives under /app: every URL below /app answers with the same
index.html and React Router draws the page. When the last Jinja page is gone, this moves to "/" (see the
basename in frontend/src/main.tsx). The app is not behind login_required on purpose: its own RequireAuth sends
anyone who is not logged in to /app/login.
"""
from pathlib import Path

from flask import Blueprint, send_file

spa_bp = Blueprint('spa', __name__)

BUILD = Path(__file__).resolve().parent.parent / 'static' / 'app'


@spa_bp.get('/app', defaults={'path': ''}, strict_slashes=False)
@spa_bp.get('/app/<path:path>')
def shell(path):
    index = BUILD / 'index.html'
    if not index.exists():
        return 'The React app is not built yet. Run "npm run build" in the frontend folder.', 503

    response = send_file(index)
    response.headers['Cache-Control'] = 'no-cache'  # its script and style names change with every build
    return response
