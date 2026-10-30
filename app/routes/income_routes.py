from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import income_controller as controller
from app.routes._rest import register

income_bp = Blueprint('income', __name__)


@income_bp.get('/incomes')
@login_required
def index():
    return render_template('incomes.html', nav='incomes')


# JSON: GET /api/incomes, POST /api/incomes, GET /api/incomes/<id>, PUT /api/incomes/<id>, DELETE /api/incomes/<id>
register(income_bp, controller.RESOURCE, '/incomes')
