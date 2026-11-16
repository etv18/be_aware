from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
babel = Babel()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()
crsf = CSRFProtect()