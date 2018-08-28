import os
from dotenv import find_dotenv, load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

#load .env file, environment variables can be gotten using os.environ.get('KEY')
if not load_dotenv(find_dotenv(), verbose=True):
    print('No .env file found.')


#variables.
SECRET_KEY = os.environ.get('KEY')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("KEY")
    #SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir + '/database', 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir + '/database', 'db_repository')
    MIGRATION_DIR = os.path.join(basedir + '/database', 'db_repository')

class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  #'sqlite:///' + os.path.join(basedir + '/database', 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir + '/database', 'db_repository')
    MIGRATION_DIR = os.path.join(basedir + '/database', 'db_repository')
