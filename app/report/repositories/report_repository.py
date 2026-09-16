from app.extensions import db
from app.models import Production, Payment, Product, Stage
from sqlalchemy import func


class ReportRepository:
    @staticmethod
    def _apply_period(query, start_date=None, end_date=None):
        if start_date is not None:
            query = query.filter(Production.date >= start_date)
        if end_date is not None:
            query = query.filter(Production.date <= end_date)
        return query

    @classmethod
    def production_summary(cls, start_date=None, end_date=None):
        query = db.session.query(
            func.count(Production.id).label("production_count"),
            func.coalesce(func.sum(Production.dozens), 0).label("total_dozens"),
            func.coalesce(func.sum(Production.total_amount), 0).label("total_amount"),
        )
        return cls._apply_period(query, start_date, end_date).first()

    @classmethod
    def by_product(cls, start_date=None, end_date=None, limit=None):
        aggregate = db.session.query(
            Production.product_id.label("product_id"),
            func.sum(Production.dozens).label("total_dozens"),
            func.sum(Production.total_amount).label("total_amount"),
            func.count(Production.id).label("production_count"),
        )
        aggregate = cls._apply_period(aggregate, start_date, end_date)
        aggregate = aggregate.group_by(Production.product_id).subquery()

        query = (
            db.session.query(
                Product,
                aggregate.c.total_dozens,
                aggregate.c.total_amount,
                aggregate.c.production_count,
            )
            .join(aggregate, aggregate.c.product_id == Product.id)
            .order_by(aggregate.c.total_dozens.desc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def by_stage(cls, start_date=None, end_date=None, limit=None):
        aggregate = db.session.query(
            Production.stage_id.label("stage_id"),
            func.sum(Production.dozens).label("total_dozens"),
            func.sum(Production.total_amount).label("total_amount"),
            func.count(Production.id).label("production_count"),
        )
        aggregate = cls._apply_period(aggregate, start_date, end_date)
        aggregate = aggregate.group_by(Production.stage_id).subquery()

        query = (
            db.session.query(
                Stage,
                aggregate.c.total_dozens,
                aggregate.c.total_amount,
                aggregate.c.production_count,
            )
            .join(aggregate, aggregate.c.stage_id == Stage.id)
            .order_by(aggregate.c.total_dozens.desc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def by_day(cls, start_date=None, end_date=None, descending=False):
        query = db.session.query(
            Production.date,
            func.sum(Production.dozens).label("total_dozens"),
            func.sum(Production.total_amount).label("total_amount"),
            func.count(Production.id).label("production_count"),
        )
        query = cls._apply_period(query, start_date, end_date)
        order = Production.date.desc() if descending else Production.date.asc()
        return query.group_by(Production.date).order_by(order).all()

    @staticmethod
    def date_bounds():
        return db.session.query(
            func.min(Production.date).label("start_date"),
            func.max(Production.date).label("end_date"),
        ).first()

    @staticmethod
    def unpaid_summary():
        return db.session.query(
            func.count(Production.id).label("count"),
            func.coalesce(func.sum(Production.dozens), 0).label("dozens"),
            func.coalesce(func.sum(Production.total_amount), 0).label("amount"),
        ).filter(Production.payment_id.is_(None)).first()

    @staticmethod
    def pending_payment_summary():
        return db.session.query(
            func.count(Payment.id).label("count"),
            func.coalesce(func.sum(Payment.total_amount), 0).label("amount"),
        ).filter(Payment.status == "pending").first()

    @staticmethod
    def paid_amount(start_date=None, end_date=None):
        query = db.session.query(func.coalesce(func.sum(Payment.total_amount), 0)).filter(
            Payment.status == "paid"
        )
        if start_date is not None:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date is not None:
            query = query.filter(Payment.payment_date <= end_date)
        return query.scalar()

    @staticmethod
    def recent_productions(limit=5):
        return (
            db.session.query(Production)
            .order_by(Production.date.desc(), Production.id.desc())
            .limit(limit)
            .all()
        )


report_repository = ReportRepository()
