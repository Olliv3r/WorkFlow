from datetime import date
from decimal import Decimal
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ConflictError
from app.payment.repositories import *
from app.models import Payment, DailyWork, Advance, AdvanceDeduction, ReceiptAllocation
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
        productions = PaymentService.get_productions(start_date, end_date)
        daily_works = PaymentService.get_daily_works(start_date, end_date)
        dates = [p.date for p in productions] + [d.date for d in daily_works]
        if not dates:
            return None, None
        return min(dates), max(dates)

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
        # The POSTed checkbox IDs are the only source of truth. Never rebuild
        # a closing from all unpaid rows in the period.
        productions = production_repository.filter_by_ids(ids).filter(
            production_repository.model.payment_id.is_(None)
        ).all() if ids else []
        daily_works = DailyWork.query.filter(
            DailyWork.id.in_(daily_work_ids), DailyWork.payment_id.is_(None)
        ).all() if daily_work_ids else []
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
            status="closed", observation=(observation or "").strip() or None)
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
                    db.session.add(AdvanceDeduction(advance=advance, payment=payment, amount=amount, kind="closing"))
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
        if payment.receipt_allocations:
            raise PermissionError("Não é possível excluir um fechamento que já possui recebimentos. O histórico financeiro está protegido.")

        try:
            for production in payment.productions:
                production.payment_id = None
            for daily_work in payment.daily_works:
                daily_work.payment_id = None
            payment_repository.delete(payment)
            payment_repository.commit()
        except Exception:
            payment_repository.session.rollback()
            raise
        return True

    @staticmethod
    def toggle_status(payment_id: int):
        raise ValidationError("O status agora é calculado pelos recebimentos. Registre o valor efetivamente recebido.")

    @staticmethod
    def get_receivables_summary():
        """Resumo financeiro sem inventar FIFO para recebimentos."""
        from app.models import Receipt
        payments = Payment.query.order_by(Payment.start_period.asc(), Payment.id.asc()).all()
        due = sum((p.net_amount for p in payments), Decimal("0.00"))
        received = db.session.query(func.coalesce(func.sum(Receipt.amount), 0)).scalar() or Decimal("0.00")
        receivable_advances = sum((p.receivable_advance_amount for p in payments), Decimal("0.00"))
        balance = due - received - receivable_advances
        if balance < 0:
            balance = Decimal("0.00")
        identified = sum((p.pending_amount for p in payments), Decimal("0.00"))
        unallocated = db.session.query(func.coalesce(func.sum(Receipt.amount), 0)).scalar() or Decimal("0.00")
        allocated = db.session.query(func.coalesce(func.sum(ReceiptAllocation.amount), 0)).scalar() or Decimal("0.00")
        return {
            "total_due": due,
            "total_received": received,
            "balance": balance,
            "identified_pending": identified,
            "unallocated_received": max(Decimal("0.00"), unallocated - allocated),
        }

    @staticmethod
    def register_receipt(amount, receipt_date=None, observation=None, payment_id=None, allocations=None):
        """Registra dinheiro recebido e, quando conhecido, distribui-o entre fechamentos.

        ``allocations`` aceita uma lista de dicionários com ``payment_id`` e
        ``amount``. O total alocado pode ser menor que o valor recebido; nesse
        caso, a diferença permanece como recebimento sem origem identificada.

        ``payment_id`` foi mantido para compatibilidade com o formulário da
        página de detalhes de um único fechamento.
        """
        from app.models import Receipt, ReceiptAllocation

        def parse_money(value, field_name):
            try:
                parsed = Decimal(str(value).strip().replace(",", "."))
            except Exception:
                raise ValidationError(f"{field_name} inválido")
            if not parsed.is_finite():
                raise ValidationError(f"{field_name} inválido")
            return parsed.quantize(Decimal("0.01"))

        amount = parse_money(amount, "Valor recebido")
        if amount <= 0:
            raise ValidationError("O valor recebido deve ser maior que zero")

        if receipt_date in (None, ""):
            receipt_date = date.today()
        elif isinstance(receipt_date, str):
            try:
                receipt_date = date.fromisoformat(receipt_date)
            except ValueError:
                raise ValidationError("Data de recebimento inválida")

        raw_allocations = list(allocations or [])
        # Compatibilidade: a tela de detalhes continua enviando apenas payment_id.
        if not raw_allocations and payment_id not in (None, ""):
            raw_allocations = [{"payment_id": payment_id, "amount": amount}]

        normalized_allocations = []
        seen_payment_ids = set()
        allocated_total = Decimal("0.00")

        for item in raw_allocations:
            try:
                allocation_payment_id = int(item.get("payment_id"))
            except (TypeError, ValueError, AttributeError):
                raise ValidationError("Pagamento selecionado inválido")

            if allocation_payment_id in seen_payment_ids:
                raise ValidationError("O mesmo pagamento foi selecionado mais de uma vez")
            seen_payment_ids.add(allocation_payment_id)

            allocation_amount = parse_money(item.get("amount"), "Valor da alocação")
            if allocation_amount <= 0:
                raise ValidationError("O valor destinado a cada pagamento deve ser maior que zero")

            payment = PaymentService.get_payment(allocation_payment_id)
            pending_amount = payment.pending_amount
            if allocation_amount > pending_amount:
                raise ValidationError(
                    f"O pagamento #{payment.id} possui apenas R$ {pending_amount:.2f} pendentes"
                )

            normalized_allocations.append((payment, allocation_amount))
            allocated_total += allocation_amount

        if allocated_total > amount:
            raise ValidationError(
                f"A soma destinada aos pagamentos (R$ {allocated_total:.2f}) "
                f"não pode ultrapassar o valor recebido (R$ {amount:.2f})"
            )

        receipt = Receipt(
            date=receipt_date,
            amount=amount,
            observation=(observation or "").strip() or None,
        )
        try:
            db.session.add(receipt)
            db.session.flush()
            for payment, allocation_amount in normalized_allocations:
                db.session.add(ReceiptAllocation(
                    receipt=receipt, payment=payment, amount=allocation_amount
                ))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return receipt

    @staticmethod
    def get_receipts():
        from app.models import Receipt
        return Receipt.query.order_by(Receipt.date.desc(), Receipt.id.desc()).all()
