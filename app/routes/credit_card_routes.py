from flask import Blueprint, render_template
from flask_login import login_required

from app.controllers import credit_card_controller as controller
from app.routes._rest import get, register

credit_card_bp = Blueprint('credit_card', __name__)


@credit_card_bp.get('/credit_cards')
@login_required
def index():
    return render_template('credit_cards.html', nav='cards')


@credit_card_bp.get('/credit_cards/<int:record_id>')
@login_required
def show(record_id):
    return render_template('credit_card.html', nav='cards', id=record_id)


# JSON: GET /api/credit_cards, POST /api/credit_cards, GET /api/credit_cards/<id>, PUT /api/credit_cards/<id>, DELETE /api/credit_cards/<id>
register(credit_card_bp, controller.RESOURCE, '/credit_cards')

# what hangs from a card, and its yearly report (GET, ?year=2026)
get(credit_card_bp, '/credit_cards/<int:card_id>/records', controller.records_of, 'records')
get(credit_card_bp, '/credit_cards/<int:card_id>/reports/yearly', controller.yearly_report, 'yearly')
