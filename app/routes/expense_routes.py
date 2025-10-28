from flask import request, redirect, url_for, render_template, Blueprint

from app.models.expense import Expense
from app.controllers import expense_controller

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

@expense_bp.route('/index', methods=['GET'])
def index():

    return render_template('expenses/index.html')