import pytest

from app import create_app
from app.extensions import db
from app.seed.services.seed_service import SeedService


class TestConfig:
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "workflow-test.db"
    TestConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded(app):
    with app.app_context():
        seed_all()
    return app


def seed_all():
    seed = SeedService()
    seed.create_product_families()
    seed.create_materials()
    seed.create_qualities()
    seed.create_holes()
    seed.create_stick_types()
    seed.create_stages()
    seed.create_products()
