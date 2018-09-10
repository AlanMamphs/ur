import os

APP_ROOT = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	DEBUG=False
	TESTING=False
	CSRF_ENABLED=True
	SECRET_KEY='this-really-needs-to-be-changed'
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	UPLOADED_PHOTOS_DEST = 'static/media'


class StagingConfig(Config):
	DEVELOPMENT = True
	DEBUG = True

class ProductionConfig(Config):
	DEBUG = False

class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True


class TestingConfig(Config):
	TESTING=True
