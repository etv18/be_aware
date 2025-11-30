from flask import Blueprint, render_template, redirect, url_for, request, jsonify

accounts_receivable_bp = Blueprint('accounts_receivable', __name__, url_prefix='/accounts_receivable')

@accounts_receivable_bp.route('/index', methods=['GET'])
def index():
    return render_template('accounts_receivable/index.html')