import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'America/Santo_Domingo'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY')