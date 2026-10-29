import os

from dotenv import load_dotenv

load_dotenv()

# Project root (the folder that contains run.py). Flask's instance folder lives here too.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')


def _sqlite_uri(filename):
    """Build a sqlite URI for a file inside the instance folder (forward slashes work on Windows too)."""
    return 'sqlite:///' + os.path.join(INSTANCE_DIR, filename).replace('\\', '/')


class Config:
    """Settings shared by every environment. Nothing here is environment specific."""

    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'America/Santo_Domingo'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY')

    NAV_BAR_BACKGROUND_COLOR = os.getenv('NAV_BAR_BACKGROUND_COLOR', 'bg-primary')

    LOG_TO_FILES = True

    # What the page shows in its badge; each environment below sets its own
    ENV_NAME = 'development'
    ENV_LABEL = 'DEV'


class DevelopmentConfig(Config):
    """Local development. Uses a SQLite file (instance/be_aware_dev.db) unless DEV_DATABASE_URL is set."""

    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    ENV_NAME, ENV_LABEL = 'development', 'DEV'

    # A throwaway key so sessions work out of the box. Never used in production.
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-only-insecure-key'
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL') or _sqlite_uri('be_aware_dev.db')


class TestingConfig(Config):
    """Used by pytest. In-memory SQLite by default, so every test starts from an empty database."""

    TESTING = True
    LOG_TO_FILES = False
    ENV_NAME, ENV_LABEL = 'testing', 'TEST'

    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL') or 'sqlite:///:memory:'

    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Real deployment. Reads the MySQL connection from the .env file (see app/utils/db.py)."""

    ENV_NAME, ENV_LABEL = 'production', 'PROD'

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # Imported here so development and tests never need the DB_* variables.
        from app.utils.db import db_url
        return db_url


_CONFIGS = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}


def get_config(name=None):
    """Return a config object. `name` falls back to the APP_ENV variable, then to 'development'."""
    name = (name or os.getenv('APP_ENV') or 'development').lower()

    try:
        return _CONFIGS[name]()
    except KeyError:
        raise RuntimeError(
            f"Unknown APP_ENV '{name}'. Use one of: {', '.join(sorted(_CONFIGS))}."
        )
