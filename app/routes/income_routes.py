from flask import Blueprint, redirect, render_template, request, url_for

from app.models.income import Income

income_bp = Blueprint('income', __name__, url_prefix='/incomes')

@income_bp.route('/index', methods=['GET', 'POST'])
def index():

    return render_template('incomes/index.html')
