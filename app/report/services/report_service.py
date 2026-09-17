from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from app.payment.repositories import payment_repository
from app.report.repositories import report_repository


class ReportService:
    @staticmethod
    def get_pending_summary():
        return payment_repository.get_pending_summary().first()

    @staticmethod
    def get_pending_payments():
        return payment_repository.get_pending().all()

    @staticmethod
    def production_summary(start_date=None, end_date=None):
        return report_repository.production_summary(start_date, end_date)

    @staticmethod
    def by_product(start_date=None, end_date=None, limit=None):
        return report_repository.by_product(start_date, end_date, limit=limit)

    @staticmethod
    def by_stage(start_date=None, end_date=None, limit=None):
        return report_repository.by_stage(start_date, end_date, limit=limit)

    @staticmethod
    def by_day(start_date=None, end_date=None):
        return report_repository.by_day(start_date, end_date, descending=True)

    @staticmethod
    def dashboard_data(today=None):
        today = today or date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        product_rows = report_repository.by_product(month_start, today, limit=5)
        return {
            "today_summary": report_repository.production_summary(today, today),
            "week_summary": report_repository.production_summary(week_start, today),
            "month_summary": report_repository.production_summary(month_start, today),
            "unpaid": report_repository.unpaid_summary(),
            "pending": report_repository.pending_payment_summary(),
            "paid_month": report_repository.paid_amount(month_start, today),
            "top_products": [(product, dozens) for product, dozens, _amount, _count in product_rows],
            "recent": report_repository.recent_productions(limit=5),
            "trend": ReportService.trend(today - timedelta(days=29), today),
        }

    @staticmethod
    def _resolve_period(start_date=None, end_date=None):
        if start_date and end_date:
            return start_date, end_date

        bounds = report_repository.date_bounds()
        if not bounds or not bounds.start_date or not bounds.end_date:
            today = date.today()
            return start_date or (today - timedelta(days=29)), end_date or today

        return start_date or bounds.start_date, end_date or bounds.end_date

    @staticmethod
    def _next_month(value):
        if value.month == 12:
            return date(value.year + 1, 1, 1)
        return date(value.year, value.month + 1, 1)

    @staticmethod
    def _format_bucket(bucket, granularity):
        if granularity == "day":
            return bucket.strftime("%d/%m")
        if granularity == "month":
            return bucket.strftime("%m/%Y")
        return str(bucket.year)

    @staticmethod
    def trend(start_date=None, end_date=None):
        start_date, end_date = ReportService._resolve_period(start_date, end_date)
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        rows = report_repository.by_day(start_date, end_date, descending=False)
        span = (end_date - start_date).days
        granularity = "day" if span <= 62 else "month" if span <= 730 else "year"
        values = defaultdict(lambda: {"dozens": 0, "amount": Decimal("0.00")})

        for day, dozens, amount, _count in rows:
            if granularity == "day":
                bucket = day
            elif granularity == "month":
                bucket = date(day.year, day.month, 1)
            else:
                bucket = date(day.year, 1, 1)
            values[bucket]["dozens"] += int(dozens or 0)
            values[bucket]["amount"] += Decimal(amount or 0)

        buckets = []
        if granularity == "day":
            cursor = start_date
            while cursor <= end_date:
                buckets.append(cursor)
                cursor += timedelta(days=1)
        elif granularity == "month":
            cursor = date(start_date.year, start_date.month, 1)
            last = date(end_date.year, end_date.month, 1)
            while cursor <= last:
                buckets.append(cursor)
                cursor = ReportService._next_month(cursor)
        else:
            buckets = [date(year, 1, 1) for year in range(start_date.year, end_date.year + 1)]

        return {
            "granularity": granularity,
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "items": [
                {
                    "label": ReportService._format_bucket(bucket, granularity),
                    "dozens": values[bucket]["dozens"],
                    "amount": float(values[bucket]["amount"]),
                }
                for bucket in buckets
            ],
        }

    @staticmethod
    def comparison(start_date=None, end_date=None):
        if start_date is None and end_date is None:
            end_date = date.today()
            start_date = end_date.replace(day=1)
        else:
            start_date, end_date = ReportService._resolve_period(start_date, end_date)

        if end_date < start_date:
            start_date, end_date = end_date, start_date

        days = (end_date - start_date).days + 1
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days - 1)
        current = report_repository.production_summary(start_date, end_date)
        previous = report_repository.production_summary(previous_start, previous_end)

        def change(current_value, previous_value):
            current_value = float(current_value or 0)
            previous_value = float(previous_value or 0)
            if previous_value == 0:
                return None if current_value else 0.0
            return ((current_value - previous_value) / previous_value) * 100

        return {
            "current_start": start_date,
            "current_end": end_date,
            "previous_start": previous_start,
            "previous_end": previous_end,
            "current": current,
            "previous": previous,
            "dozens_change": change(current.total_dozens, previous.total_dozens),
            "amount_change": change(current.total_amount, previous.total_amount),
        }

    @staticmethod
    def product_chart(start_date=None, end_date=None, limit=8):
        rows = report_repository.by_product(start_date, end_date, limit=limit)
        return [
            {
                "label": f"{product.family.name} — {product.material.name}" + (f" · {product.hole.quantity} furos" if product.hole else ""),
                "value": int(dozens or 0),
            }
            for product, dozens, _amount, _count in rows
        ]

    @staticmethod
    def stage_chart(start_date=None, end_date=None, limit=8):
        rows = report_repository.by_stage(start_date, end_date, limit=limit)
        return [
            {"label": stage.name, "value": int(dozens or 0)}
            for stage, dozens, _amount, _count in rows
        ]
