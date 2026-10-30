"""One error format for every JSON response:  {"error": {"code": "...", "message": "...", "fields": {...}}}

`code` is stable and meant for programs (a React app can switch on it); `message` is for people.
A request counts as JSON when it goes to /api, sends JSON, asks for JSON, or changes data (POST, PUT, DELETE);
a person opening a page in the browser still gets the normal HTML error pages.
"""
import re

from flask import current_app, jsonify, render_template, request
from flask_wtf.csrf import CSRFError
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.exceptions.records import RecordNotFound


def wants_json():
    if request.path.startswith('/api/') or request.method not in ('GET', 'HEAD'):
        return True
    return request.is_json or request.accept_mimetypes.best == 'application/json'


def error_response(status, code, message, fields=None):
    body = {'code': code, 'message': message}
    if fields:
        body['fields'] = fields
    return jsonify({'error': body}), status


def _snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


# pydantic's technical messages, as a person would say them
FRIENDLY = {
    'missing': 'This field is required.',
    'string_too_short': 'This field is required.',
    'string_too_long': 'This text is too long.',
    'decimal_parsing': 'Enter a valid amount.',
    'decimal_type': 'Enter a valid amount.',
    'int_parsing': 'Choose an option.',
    'int_type': 'Choose an option.',
    'bool_parsing': 'Choose yes or no.',
    'bool_type': 'Choose yes or no.',
    'datetime_parsing': 'Enter a valid date and time.',
    'datetime_from_date_parsing': 'Enter a valid date and time.',
    'datetime_type': 'Enter a valid date and time.',
}


def _validation_fields(error):
    fields = {}
    for item in error.errors():
        name = '.'.join(str(part) for part in item['loc']) or 'body'
        message = FRIENDLY.get(item['type']) or item['msg'].removeprefix('Value error, ')
        fields.setdefault(name, message)
    return fields


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def _invalid(error):
        fields = _validation_fields(error)
        first = next(iter(fields.items()), ('body', 'Invalid data'))
        return error_response(422, 'validation_error', f'{first[0]}: {first[1]}', fields)

    @app.errorhandler(RecordNotFound)
    def _not_found(error):
        return error_response(404, 'not_found', str(error))

    @app.errorhandler(CSRFError)
    def _csrf(error):
        return error_response(400, 'csrf_failed', 'The security token is missing or has expired. Reload the page.')

    @app.errorhandler(HTTPException)
    def _http(error):
        if not wants_json():
            return error
        return error_response(error.code or 500, _snake(error.name.replace(' ', '')), error.description)

    @app.errorhandler(ValueError)
    def _value(error):
        return error_response(400, 'invalid_value', str(error))

    @app.errorhandler(Exception)
    def _any(error):
        # the money services raise small domain exceptions (NoAvailableMoney, LoanAlreadyPaid ...):
        # their message is written for the person, their class name makes the code
        if type(error).__module__.startswith('app.exceptions'):
            return error_response(400, _snake(type(error).__name__), str(error))

        if not wants_json():
            raise error
        current_app.logger.exception('Unexpected error')
        return error_response(500, 'server_error', 'Something went wrong on the server.')


def unauthorized():
    """Flask-Login: JSON callers get a 401, a person opening a page gets the login form."""
    if wants_json():
        return error_response(401, 'not_authenticated', 'You need to log in.')
    return render_template('auth/login.html')
