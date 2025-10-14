from flask import Blueprint, render_template

bank_bp = Blueprint('bank', __name__, url_prefix='/banks')

@bank_bp.route('/index')
def index():
    return render_template('banks/index.html')