from app.extensions import db
from app.models import ProductFamily, Material, Quality, Hole, StickType, Stage, Product
from app.seed.seed_dict import STAGES
from app.seed.services.seed_service import SeedService


def test_full_seed_runs_on_empty_database(app):
    with app.app_context():
        seed = SeedService()
        seed.create_product_families()
        seed.create_materials()
        seed.create_qualities()
        seed.create_holes()
        seed.create_stick_types()
        seed.create_stages()
        seed.create_products()

        assert db.session.query(ProductFamily).count() == 7
        assert db.session.query(Material).count() == 4
        assert db.session.query(Quality).count() == 3
        assert db.session.query(Hole).count() == 3
        assert db.session.query(StickType).count() == 5
        assert db.session.query(Stage).count() == 8
        assert db.session.query(Product).count() == 13


def test_create_stages_is_idempotent_and_uses_expected_seed(app):
    with app.app_context():
        SeedService.create_stages()
        SeedService.create_stages()

        stages = db.session.query(Stage).order_by(Stage.order.asc()).all()
        assert [stage.name for stage in stages] == [item["name"] for item in STAGES]
        assert len(stages) == len(STAGES)
