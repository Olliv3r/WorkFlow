from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import Product, Production, Stage
from app.report.services.report_service import ReportService


def _add_production(product, stage, day, dozens, price="2.00"):
    price = Decimal(price)
    production = Production(
        date=day,
        dozens=dozens,
        price_per_dozen=price,
        total_amount=price * dozens,
        product=product,
        stage=stage,
    )
    db.session.add(production)
    db.session.commit()
    return production


def test_trend_fills_days_without_production(seeded):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        _add_production(product, stage, date(2026, 9, 1), 4)
        _add_production(product, stage, date(2026, 9, 3), 6)

        trend = ReportService.trend(date(2026, 9, 1), date(2026, 9, 3))

        assert trend["granularity"] == "day"
        assert [item["dozens"] for item in trend["items"]] == [4, 0, 6]
        assert [item["label"] for item in trend["items"]] == ["01/09", "02/09", "03/09"]


def test_trend_changes_to_monthly_for_long_periods(seeded):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        _add_production(product, stage, date(2025, 1, 10), 5)
        _add_production(product, stage, date(2025, 4, 10), 7)

        trend = ReportService.trend(date(2025, 1, 1), date(2025, 4, 30))

        assert trend["granularity"] == "month"
        assert [item["dozens"] for item in trend["items"]] == [5, 0, 0, 7]


def test_period_comparison_uses_equivalent_previous_period(seeded):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        _add_production(product, stage, date(2026, 9, 1), 20)
        _add_production(product, stage, date(2026, 8, 31), 10)

        comparison = ReportService.comparison(date(2026, 9, 1), date(2026, 9, 1))

        assert comparison["current"].total_dozens == 20
        assert comparison["previous"].total_dozens == 10
        assert comparison["dozens_change"] == 100.0


def test_chart_labels_include_holes(seeded):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        _add_production(product, stage, date(2026, 9, 1), 3)

        chart = ReportService.product_chart(date(2026, 9, 1), date(2026, 9, 1))

        assert chart
        assert f"{product.hole.quantity} furos" in chart[0]["label"]
