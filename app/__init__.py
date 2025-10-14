from flask import Flask
from flask_migrate import Migrate

from app.config import Config
from app.extensions import db
from app.routes import home_routes, bank_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_resources(app)

    from app import models

    return app

def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)

def register_resources(app):
    app.register_blueprint(home_routes.home_bp)
    app.register_blueprint(bank_routes.bank_bp)
    