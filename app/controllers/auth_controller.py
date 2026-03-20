from flask import request, render_template, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, current_user

from app.models.user import User

def authenticate_user():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter(User.username == username).first()

    if not user or not verify_password(user.password, password):
        return render_template('auth/login.html', error='Wrong username or password.')
    
    login_user(user)

    return redirect(url_for('home.index'))
