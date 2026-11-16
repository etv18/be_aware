from flask import Blueprint

from app.controllers import credit_card_controller as controller
from app.controllers.out import CardYearlyOut, CreditCardRecordsOut
from app.routes._rest import get, register

credit_card_bp = Blueprint('credit_card', __name__)


# JSON: GET /api/credit_cards, POST /api/credit_cards, GET /api/credit_cards/<id>, PUT /api/credit_cards/<id>, DELETE /api/credit_cards/<id>
register(credit_card_bp, controller.RESOURCE, '/credit_cards')

# what hangs from a card, and its yearly report (GET, ?year=2026)
get(credit_card_bp, '/credit_cards/<int:card_id>/records', controller.records_of, 'records', out=CreditCardRecordsOut)
get(credit_card_bp, '/credit_cards/<int:card_id>/reports/yearly', controller.yearly_report, 'yearly', out=CardYearlyOut, query=('year',))
