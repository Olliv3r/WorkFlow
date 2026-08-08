from datetime import datetime, date
from app.core.exceptions import NotFoundError, ValidationError
from app.payment.repositories import *
from app.models import Payment

class PaymentService:
    @staticmethod
    def get_payments():
        return payment_repository.all()

    @staticmethod
    def get_productions():
        return production_repository.filter_by(payment_id=None).all()

    @staticmethod
    def get_unpaid_summary():
        return production_repository.get_unpaid_summary().first()

    @staticmethod
    def get_period():
        result = production_repository.get_unpaid().first()
  
        return result.start_period, result.end_period

    @staticmethod
    def payment_create(ids: list[int]):
        productions = production_repository.filter_by_ids(ids).all()

        if not productions:
            raise NotFoundError("Nenhuma produção encontrada")

        start_period = min(p.date for p in productions)
        end_period = max(p.date for p in productions)

        total_dozens = sum([p.dozens for p in productions])
        total_amount = sum([p.total_amount for p in productions])

        payment = Payment(
            start_period=start_period,
            end_period=end_period,
            total_dozens=total_dozens,
            total_amount=total_amount
        )

        payment_repository.add(payment)

        for production in productions:
            production.payment = payment

        payment_repository.commit()

        return payment

    @staticmethod
    def toggle_status(payment_id: int):
        payment = payment_repository.filter_by(id=payment_id).first()
        
        if payment is None:
            raise NotFoundError("Pagamento não encontrado")

        if payment.status == "pending":
            payment.status = "paid"
            payment.payment_date = date.today()
          
        elif payment.status == "paid":
            payment.status = "pending"
            payment.payment_date = None

        else:
            raise ValidationError("Status inválido de pagamento")

        payment_repository.commit()

        return payment
