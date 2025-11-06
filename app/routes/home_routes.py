from flask import Blueprint, render_template, request, jsonify

home_bp = Blueprint('home', __name__,url_prefix='/home')

@home_bp.route('/index')
def index():
    return render_template('home/index.html')