"""Login, logout and who is logged in. The page keeps its session in a cookie; the CSRF token comes from /api/session."""
from flask import jsonify, request
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import generate_csrf

from app.controllers.schemas import LoginIn
from app.errors import error_response
from app.models.user import User
from app.utils.auth import verify_password


def session_info():
    user = {'id': current_user.id, 'username': current_user.username} if current_user.is_authenticated else None
    return jsonify({'data': {'authenticated': user is not None, 'user': user, 'csrf_token': generate_csrf()}})


def login():
    credentials = LoginIn.model_validate(request.get_json(silent=True) or {})
    user = User.query.filter(User.username == credentials.username).first()

    if not user or not verify_password(user.password, credentials.password):
        return error_response(401, 'wrong_credentials', 'Wrong username or password.')

    login_user(user)
    return jsonify({'data': {'id': user.id, 'username': user.username}})


def logout():
    logout_user()
    return '', 204
