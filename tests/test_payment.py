from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.exceptions import ConflictError, ValidationError
from app.extensions import db
from app.models import Product, Stage, Production, Payment, Receipt, ReceiptAllocation
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


def _make_payment(amount, payment_date=date(2026, 9, 10)):
    amount = Decimal(amount)
    payment = Payment(
        start_period=payment_date,
        end_period=payment_date,
        total_amount=amount,
        gross_amount=amount,
        advance_amount=Decimal("0.00"),
        net_amount=amount,
        total_dozens=0,
        status="closed",
    )
    db.session.add(payment)
    db.session.commit()
    return payment


def test_receipt_can_be_allocated_to_multiple_payments_and_leave_one_out(app):
    with app.app_context():
        p1 = _make_payment("40.00", date(2026, 9, 1))
        p2 = _make_payment("100.00", date(2026, 9, 2))
        p3 = _make_payment("60.00", date(2026, 9, 3))

        receipt = PaymentService.register_receipt(
            "110,00",
            "2026-09-17",
            "Recebimento combinado",
            allocations=[
                {"payment_id": p1.id, "amount": "40,00"},
                {"payment_id": p2.id, "amount": "70,00"},
            ],
        )

        assert receipt.amount == Decimal("110.00")
        assert receipt.allocated_amount == Decimal("110.00")
        assert receipt.unallocated_amount == Decimal("0.00")
        assert len(receipt.allocations) == 2
        assert p1.pending_amount == Decimal("0.00")
        assert p2.pending_amount == Decimal("30.00")
        assert p3.pending_amount == Decimal("60.00")


def test_receipt_can_quit_all_selected_payments(app):
    with app.app_context():
        p1 = _make_payment("40.00", date(2026, 9, 1))
        p2 = _make_payment("100.00", date(2026, 9, 2))
        p3 = _make_payment("60.00", date(2026, 9, 3))

        receipt = PaymentService.register_receipt(
            "200.00",
            allocations=[
                {"payment_id": p1.id, "amount": "40.00"},
                {"payment_id": p2.id, "amount": "100.00"},
                {"payment_id": p3.id, "amount": "60.00"},
            ],
        )

        assert receipt.allocated_amount == Decimal("200.00")
        assert all(payment.pending_amount == 0 for payment in (p1, p2, p3))


def test_receipt_rejects_allocation_above_payment_pending_amount(app):
    with app.app_context():
        payment = _make_payment("50.00")

        with pytest.raises(ValidationError):
            PaymentService.register_receipt(
                "60.00",
                allocations=[{"payment_id": payment.id, "amount": "60.00"}],
            )

        assert db.session.query(Receipt).count() == 0
        assert db.session.query(ReceiptAllocation).count() == 0


def test_receipt_rejects_allocations_above_received_total(app):
    with app.app_context():
        p1 = _make_payment("60.00", date(2026, 9, 1))
        p2 = _make_payment("60.00", date(2026, 9, 2))

        with pytest.raises(ValidationError):
            PaymentService.register_receipt(
                "100.00",
                allocations=[
                    {"payment_id": p1.id, "amount": "60.00"},
                    {"payment_id": p2.id, "amount": "50.00"},
                ],
            )

        assert db.session.query(Receipt).count() == 0


def test_receipt_may_keep_unallocated_remainder(app):
    with app.app_context():
        payment = _make_payment("40.00")
        receipt = PaymentService.register_receipt(
            "50.00",
            allocations=[{"payment_id": payment.id, "amount": "40.00"}],
        )

        assert receipt.allocated_amount == Decimal("40.00")
        assert receipt.unallocated_amount == Decimal("10.00")
        assert payment.pending_amount == Decimal("0.00")


def test_receipt_create_route_accepts_multiple_allocations(app):
    with app.app_context():
        p1 = _make_payment("40.00", date(2026, 9, 1))
        p2 = _make_payment("100.00", date(2026, 9, 2))
        p1_id, p2_id = p1.id, p2.id

    client = app.test_client()
    response = client.post(
        "/payment/receipt/create",
        data={
            "date": "2026-09-17",
            "amount": "90,00",
            "allocation_payment_ids": [str(p1_id), str(p2_id)],
            f"allocation_amount_{p1_id}": "40,00",
            f"allocation_amount_{p2_id}": "50,00",
        },
    )

    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["allocated_amount"] == 90.0
    assert payload["unallocated_amount"] == 0.0

    with app.app_context():
        p1 = db.session.get(Payment, p1_id)
        p2 = db.session.get(Payment, p2_id)
        assert p1.pending_amount == Decimal("0.00")
        assert p2.pending_amount == Decimal("50.00")
