from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from sqlalchemy import func

from app.models.debt import Debt
from app.controllers import debt_controller as controller

debt_bp = Blueprint('debt', __name__, url_prefix='/debts')

@debt_bp.route('/index')
def index():
    debts = Debt.query.all()
    context = {
        'debts': debts,
    }
    render_template('debts/index.html', **context)