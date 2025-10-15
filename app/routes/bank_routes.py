from flask import Blueprint, render_template

bank_bp = Blueprint('bank', __name__, url_prefix='/banks')

@bank_bp.route('/index', methods=['GET'])
def index():
    return render_template('banks/index.html')

@bank_bp.route('/create', methods=['GET', 'POST'])
def create():
    return render_template('banks/create.html')