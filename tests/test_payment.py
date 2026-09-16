from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.exceptions import ConflictError
from app.extensions import db
from app.models import Product, Stage, Production, Payment
from app.payment.services.payment_service import PaymentService
from app.payment.views import _quick_period


def _make_production(product, stage, production_date, dozens, price):
    production = Production(
        date=production_date,
        dozens=dozens,
        price_per_dozen=Decimal(price),
        total_amount=Decimal("999.99"),  # propositalmente incorreto
        product=product,
        stage=stage,
    )
    db.session.add(production)
    db.session.commit()
    return production


def test_payment_recalculates_totals_from_persisted_source_fields(seeded):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        p1 = _make_production(product, stage, date(2026, 9, 1), 10, "2.50")
        p2 = _make_production(product, stage, date(2026, 9, 5), 4, "3.00")

        payment = PaymentService.payment_create([p1.id, p2.id])

        assert payment.total_dozens == 14
        assert payment.total_amount == Decimal("37.00")
        assert payment.start_period == date(2026, 9, 1)
        assert payment.end_period == date(2026, 9, 5)
        assert {p.id for p in payment.productions} == {p1.id, p2.id}


def test_same_production_cannot_be_paid_twice(seeded):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        production = _make_production(product, stage, date(2026, 9, 1), 10, "2.50")

        PaymentService.payment_create([production.id])
        with pytest.raises(ConflictError):
            PaymentService.payment_create([production.id])

        assert db.session.query(Payment).count() == 1


@pytest.mark.parametrize("span_days", [6, 14, 29])
def test_payment_period_supports_weekly_fortnightly_and_monthly_spans(seeded, span_days):
    with seeded.app_context():
        product = db.session.query(Product).first()
        stage = db.session.query(Stage).first()
        start = date(2026, 8, 1)
        end = start + timedelta(days=span_days)
        p1 = _make_production(product, stage, start, 1, "2.00")
        p2 = _make_production(product, stage, end, 1, "2.00")

        payment = PaymentService.payment_create([p1.id, p2.id])
        assert payment.start_period == start
        assert payment.end_period == end
        assert payment.total_dozens == 2
        assert payment.total_amount == Decimal("4.00")


def test_quick_periods_are_consistent_with_today():
    today = date.today()
    assert _quick_period("today") == (today, today)

    week_start = today - timedelta(days=today.weekday())
    assert _quick_period("this_week") == (week_start, today)
    assert _quick_period("last_week") == (week_start - timedelta(days=7), week_start - timedelta(days=1))
    assert _quick_period("last_15") == (today - timedelta(days=14), today)
    assert _quick_period("this_month") == (today.replace(day=1), today)
