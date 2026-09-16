from os import getenv
from os.path import abspath, join, dirname

BASE_DIR = abspath(dirname(__file__))
DEFAULT_DB_URL = "sqlite:///" + join(BASE_DIR, "dev.db")


def normalize_database_url(url: str) -> str:
    """Normalize common provider URLs to the drivers supported by WorkFlow.

    Explicit SQLAlchemy driver URLs (for example postgresql+psycopg://) are
    preserved. This keeps SQLite as the default while allowing a future move
    to PostgreSQL or MySQL through DATABASE_URL only.
    """
    if not url:
        return DEFAULT_DB_URL
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    if url.startswith("mysql://"):
        return "mysql+pymysql://" + url[len("mysql://"):]
    return url


DATABASE_URL = normalize_database_url(getenv("DATABASE_URL", DEFAULT_DB_URL))
DATABASE_BACKEND = DATABASE_URL.split(":", 1)[0].split("+", 1)[0]


class Config:
    SECRET_KEY = getenv("SECRET_KEY", "cattac")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {} if DATABASE_BACKEND == "sqlite" else {"pool_pre_ping": True}
    )
    BOOTSTRAP_SERVE_LOCAL = True
