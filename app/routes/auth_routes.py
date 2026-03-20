from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from app.extensions import limiter

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
@limiter.limit('6 per minute')
@limiter.limit('20 per hour')
def login():
    return 'hi'