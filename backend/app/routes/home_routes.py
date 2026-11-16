from flask import Blueprint

from app.controllers import home_controller
from app.controllers.out import DashboardOut, OptionsOut
from app.routes._rest import get

home_bp = Blueprint('home', __name__)


# JSON: the figures of the home page and the lists the forms choose from
get(home_bp, '/dashboard', home_controller.dashboard, 'dashboard', out=DashboardOut, summary='The figures of the home page')
get(home_bp, '/options', home_controller.options, 'options', out=OptionsOut, summary='The lists the form selects choose from')
