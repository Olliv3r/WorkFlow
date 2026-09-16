from datetime import date
from decimal import Decimal

import pytest

from app.core.exceptions import PermissionError as AppPermissionError
from app.extensions import db
from app.models import Product, Stage, Production, Price
from app.payment.services.payment_service import PaymentService
from app.production.dtos.production_dto import ProductionCreateDTO
from app.production.services.production_service import ProductionService
from app.production.utils.serializers import serialize_production
from app.production.views import _date_field, _decimal_field


def _first_product_stage():
    product = db.session.query(Product).order_by(Product.id.asc()).first()
    stage = db.session.query(Stage).order_by(Stage.order.asc()).first()
    return product, stage


def _dto(product, stage, *, dozens=10, price="2.50", production_date=date(2026, 9, 1), observation=None):
    return ProductionCreateDTO(
        product_id=product.id,
        stage_id=stage.id,
        dozens=dozens,
        price_per_dozen=Decimal(price),
        date=production_date,
        observation=observation,
    )


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("2.50", Decimal("2.50")),
        ("2,50", Decimal("2.50")),
        (" 2,50 ", Decimal("2.50")),
    ],
)
def test_decimal_parser_accepts_dot_and_comma(raw, expected):
    assert _decimal_field({"price_per_dozen": raw}, "price_per_dozen") == expected


@pytest.mark.parametrize("raw", ["", "texto", "--", "0", "-1,00"])
def test_decimal_parser_rejects_invalid_values(raw):
    from app.core.exceptions import ValidationError

    with pytest.raises(ValidationError):
        _decimal_field({"price_per_dozen": raw}, "price_per_dozen")


def test_date_parser_accepts_iso_date_and_rejects_invalid():
    from app.core.exceptions import ValidationError

    assert _date_field({"date": "2026-09-09"}, "date") == date(2026, 9, 9)
    with pytest.raises(ValidationError):
        _date_field({"date": "09/09/2026"}, "date")
    with pytest.raises(ValidationError):
        _date_field({"date": ""}, "date")


def test_create_production_uses_manual_price_when_no_table_price(seeded):
    with seeded.app_context():
        product, stage = _first_product_stage()
        ProductionService.production_create(_dto(product, stage, dozens=8, price="2.50"))

        production = db.session.query(Production).one()
        assert production.price_per_dozen == Decimal("2.50")
        assert production.total_amount == Decimal("20.00")
        assert production.date == date(2026, 9, 1)


def test_create_production_uses_configured_price_in_backend(seeded):
    with seeded.app_context():
        product, stage = _first_product_stage()
        db.session.add(Price(product_id=product.id, stage_id=stage.id, price_per_dozen=Decimal("3.25")))
        db.session.commit()

        # Simula POST adulterado: quando há preço cadastrado, o valor da tabela
        # é a fonte autoritativa, assim como a interface já indica ao usuário.
        ProductionService.production_create(_dto(product, stage, dozens=4, price="99.99"))

        production = db.session.query(Production).one()
        assert production.price_per_dozen == Decimal("3.25")
        assert production.total_amount == Decimal("13.00")


def test_http_create_normalizes_comma_decimal(seeded):
    client = seeded.test_client()
    with seeded.app_context():
        product, stage = _first_product_stage()
        product_id, stage_id = product.id, stage.id

    response = client.post(
        "/production/create",
        data={
            "product_id": product_id,
            "stage_id": stage_id,
            "dozens": "5",
            "price_per_dozen": "2,50",
            "date": "2026-09-09",
            "observation": "teste",
        },
    )
    assert response.get_json()["status"] == "success"

    with seeded.app_context():
        production = db.session.query(Production).one()
        assert production.price_per_dozen == Decimal("2.50")
        assert production.total_amount == Decimal("12.50")


def test_http_create_rejects_invalid_decimal(seeded):
    client = seeded.test_client()
    with seeded.app_context():
        product, stage = _first_product_stage()
        product_id, stage_id = product.id, stage.id

    response = client.post(
        "/production/create",
        data={
            "product_id": product_id,
            "stage_id": stage_id,
            "dozens": "5",
            "price_per_dozen": "texto",
            "date": "2026-09-09",
        },
    )
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload["http_status"] == 422


def test_edit_updates_all_editable_fields(seeded):
    with seeded.app_context():
        products = db.session.query(Product).order_by(Product.id.asc()).limit(2).all()
        stages = db.session.query(Stage).order_by(Stage.order.asc()).limit(2).all()
        product, other_product = products
        stage, other_stage = stages

        ProductionService.production_create(_dto(product, stage, dozens=5, price="2.50"))
        production = db.session.query(Production).one()

        edit_dto = ProductionCreateDTO(
            product_id=other_product.id,
            stage_id=other_stage.id,
            dozens=6,
            price_per_dozen=Decimal("3.00"),
            date=date(2026, 9, 10),
            observation="editada",
        )
        ProductionService.edit(production.id, edit_dto)
        db.session.refresh(production)

        assert production.date == date(2026, 9, 10)
        assert production.product_id == other_product.id
        assert production.stage_id == other_stage.id
        assert production.dozens == 6
        assert production.price_per_dozen == Decimal("3.00")
        assert production.total_amount == Decimal("18.00")
        assert production.observation == "editada"
        assert serialize_production(production)["date"] == "2026-09-10"


def test_linked_production_cannot_be_edited_or_deleted(seeded):
    with seeded.app_context():
        product, stage = _first_product_stage()
        ProductionService.production_create(_dto(product, stage))
        production = db.session.query(Production).one()
        PaymentService.payment_create([production.id])

        edit_dto = _dto(product, stage, dozens=99, price="9.99", production_date=None)
        with pytest.raises(AppPermissionError):
            ProductionService.edit(production.id, edit_dto)
        with pytest.raises(AppPermissionError):
            ProductionService.production_delete(production.id)


def test_unlinked_production_can_be_deleted(seeded):
    with seeded.app_context():
        product, stage = _first_product_stage()
        ProductionService.production_create(_dto(product, stage))
        production = db.session.query(Production).one()
        assert ProductionService.production_delete(production.id) is True
        assert db.session.query(Production).count() == 0


def test_http_edit_normalizes_comma_and_changes_date(seeded):
    with seeded.app_context():
        product, stage = _first_product_stage()
        ProductionService.production_create(
            _dto(product, stage, dozens=5, price="2.50", production_date=date(2026, 9, 1))
        )
        production = db.session.query(Production).one()
        production_id = production.id
        product_id = product.id
        stage_id = stage.id

    client = seeded.test_client()
    response = client.post(
        f"/production/{production_id}/edit",
        data={
            "product_id": product_id,
            "stage_id": stage_id,
            "dozens": "7",
            "price_per_dozen": "3,50",
            "date": "2030-01-01",
            "observation": "editada via HTTP",
        },
    )
    assert response.get_json()["status"] == "success"

    with seeded.app_context():
        production = db.session.get(Production, production_id)
        assert production.date == date(2030, 1, 1)
        assert production.dozens == 7
        assert production.price_per_dozen == Decimal("3.50")
        assert production.total_amount == Decimal("24.50")


@pytest.mark.parametrize(
    "dozens, price, production_date",
    [
        (0, "2.50", date(2026, 9, 1)),
        (-1, "2.50", date(2026, 9, 1)),
        (1, "0.00", date(2026, 9, 1)),
        (1, "-2.50", date(2026, 9, 1)),
        (1, "2.50", None),
    ],
)
def test_service_rejects_invalid_create_values(seeded, dozens, price, production_date):
    from app.core.exceptions import ValidationError

    with seeded.app_context():
        product, stage = _first_product_stage()
        with pytest.raises(ValidationError):
            ProductionService.production_create(
                _dto(
                    product,
                    stage,
                    dozens=dozens,
                    price=price,
                    production_date=production_date,
                )
            )


def test_production_details_page_shows_complete_product_identity(seeded):
    with seeded.app_context():
        product, stage = _first_product_stage()
        ProductionService.production_create(_dto(product, stage, dozens=3, price="2.50"))
        production = db.session.query(Production).one()
        production_id = production.id
        expected_label = f"{product.family.name} — {product.material.name} · {product.hole.quantity} furos"

    response = seeded.test_client().get(f"/production/{production_id}/details")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert expected_label in html
    assert "Dados da produção" in html
    assert "Preço por dúzia" in html
