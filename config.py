from os import getenv
from os.path import abspath, join, dirname

BASE_DIR = abspath(dirname(__file__))
DEFAULT_DB_URL = 'sqlite:///' + join(BASE_DIR, "dev.db")

class Config:
    SECRET_KEY = getenv("SECRET_KEY", "cattac")
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL", DEFAULT_DB_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True
