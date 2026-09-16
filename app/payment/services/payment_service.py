from datetime import date
from decimal import Decimal
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ConflictError
from app.payment.repositories import *
from app.models import Payment, DailyWork, Advance, AdvanceDeduction
from app.extensions import db
from sqlalchemy import func


class PaymentService:
    @staticmethod
    def get_payments():
        return payment_repository.all(order_by="id", descending=True)

    @staticmethod
    def get_payment(payment_id: int):
        payment = payment_repository.filter_by(id=payment_id).first()
        if payment is None:
            raise NotFoundError("Pagamento não encontrado")
        return payment

    @staticmethod
    def get_productions(start_date=None, end_date=None):
        query = production_repository.filter_by(payment_id=None)
        if start_date is not None:
            query = query.filter(production_repository.model.date >= start_date)
        if end_date is not None:
            query = query.filter(production_repository.model.date <= end_date)
        return query.order_by(production_repository.model.date.asc()).all()

    @staticmethod
    def get_unpaid_summary(start_date=None, end_date=None):
        return production_repository.get_unpaid_summary(start_date, end_date).first()

    @staticmethod
    def get_period(start_date=None, end_date=None):
        query = production_repository.filter_by(payment_id=None)
        if start_date is not None:
            query = query.filter(production_repository.model.date >= start_date)
        if end_date is not None:
            query = query.filter(production_repository.model.date <= end_date)
        productions = query.all()
        if not productions:
            return None, None
        return min(p.date for p in productions), max(p.date for p in productions)

    @staticmethod
    def get_daily_works(start_date=None, end_date=None):
        query = DailyWork.query.filter_by(payment_id=None)
        if start_date is not None: query = query.filter(DailyWork.date >= start_date)
        if end_date is not None: query = query.filter(DailyWork.date <= end_date)
        return query.order_by(DailyWork.date.asc()).all()

    @staticmethod
    def payment_create(ids: list[int], observation=None, daily_work_ids=None):
        ids = list(dict.fromkeys(ids or []))
        daily_work_ids = list(dict.fromkeys(daily_work_ids or []))
        if not ids and not daily_work_ids:
            raise ValidationError("Selecione pelo menos uma produção ou diária")
        productions = production_repository.filter_by_ids(ids).all() if ids else []
        daily_works = DailyWork.query.filter(DailyWork.id.in_(daily_work_ids)).all() if daily_work_ids else []
        if len(productions) != len(ids) or len(daily_works) != len(daily_work_ids):
            raise NotFoundError("Uma ou mais remunerações não foram encontradas")
        if any(p.payment_id is not None for p in productions) or any(d.payment_id is not None for d in daily_works):
            raise ConflictError("Uma ou mais remunerações já pertencem a outro pagamento")
        dates = [p.date for p in productions] + [d.date for d in daily_works]
        total_dozens = sum(p.dozens for p in productions)
        production_total = sum((p.dozens * p.price_per_dozen for p in productions), Decimal("0.00"))
        daily_total = sum((d.total_amount for d in daily_works), Decimal("0.00"))
        gross = production_total + daily_total
        payment = Payment(start_period=min(dates), end_period=max(dates), total_dozens=total_dozens,
            total_amount=gross, gross_amount=gross, advance_amount=Decimal("0.00"), net_amount=gross,
            observation=(observation or "").strip() or None)
        try:
            payment_repository.add(payment); db.session.flush()
            for p in productions: p.payment = payment
            for d in daily_works: d.payment = payment
            remaining = gross
            advances = Advance.query.outerjoin(AdvanceDeduction).group_by(Advance.id).having(
                Advance.amount > func.coalesce(func.sum(AdvanceDeduction.amount), 0)
            ).order_by(Advance.date.asc(), Advance.id.asc()).all()
            deducted = Decimal("0.00")
            for advance in advances:
                if remaining <= 0: break
                amount = min(advance.balance, remaining)
                if amount > 0:
                    db.session.add(AdvanceDeduction(advance=advance, payment=payment, amount=amount))
                    deducted += amount; remaining -= amount
            payment.advance_amount = deducted
            payment.net_amount = gross - deducted
            payment.total_amount = payment.net_amount
            payment_repository.commit()
        except Exception:
            payment_repository.session.rollback(); raise
        return payment

    @staticmethod
    def payment_delete(payment_id: int) -> bool:
        payment = PaymentService.get_payment(payment_id)
        if payment.status != "pending":
            raise PermissionError("Não é possível excluir um pagamento já pago")

        try:
            for production in payment.productions:
                production.payment_id = None
            payment_repository.delete(payment)
            payment_repository.commit()
        except Exception:
            payment_repository.session.rollback()
            raise
        return True

    @staticmethod
    def toggle_status(payment_id: int):
        payment = PaymentService.get_payment(payment_id)
        if payment.status == "pending":
            payment.status = "paid"
            payment.payment_date = date.today()
        elif payment.status == "paid":
            raise PermissionError("Pagamento pago é histórico consolidado e não pode voltar para pendente")
        else:
            raise ValidationError("Status inválido de pagamento")
        payment_repository.commit()
        return payment
