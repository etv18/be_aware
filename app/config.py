class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///be_aware.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True