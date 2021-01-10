import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    WTF_CSRF_ENABLED = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configurations for Development Environment."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

class TestingConfig(Config):
    """Configurations for Testing Environment."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'postgresql:///dive_test'

class ProductionConfig(Config):
    """Configurations for Production Environment."""

    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}