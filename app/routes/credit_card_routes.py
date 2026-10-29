from flask import Blueprint
from flask_login import login_required

from app.controllers import credit_card_controller as controller
from app.routes._pages import page
from app.routes._rest import register

credit_card_bp = Blueprint('credit_card', __name__, url_prefix='/credit_cards')


@credit_card_bp.route('/index', methods=['GET'])
@login_required
def index():
    return page('cards', 'credit-cards', 'Credit cards')


@credit_card_bp.route('/associated_records/<int:id>', methods=['GET'])
@login_required
def associated_records(id):
    return page('cards', 'credit-card', 'Credit card', id=id)


register(credit_card_bp, controller.RESOURCE)

credit_card_bp.add_url_rule('/<int:card_id>/records', 'records', login_required(controller.records_of), methods=['GET'])
credit_card_bp.add_url_rule('/<int:card_id>/reports/yearly', 'yearly', login_required(controller.yearly_report), methods=['GET'])
