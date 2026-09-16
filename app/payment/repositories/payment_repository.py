from app.extensions import db
from sqlalchemy import func
from app.common.repositories.common_repository import CommonRepository
from app.models import Payment

class PaymentRepository(CommonRepository):
    model = Payment

    def get_pending_summary(self):
        """
        Agrega todos os pagamentos com status 'pending' — usado pelo
        relatório de "vários pagamentos pendentes" (ver
        app/report/services/report_service.py). Não altera nenhum
        registro; é leitura pura, soma o que já existe no banco.
        """
        return self.session.query(
            func.count(self.model.id).label("payment_count"),
            func.coalesce(func.sum(self.model.total_dozens), 0).label("total_dozens"),
            func.coalesce(func.sum(self.model.total_amount), 0).label("total_amount"),
        ).filter(self.model.status == "pending")

    def get_pending(self):
        """Lista os próprios pagamentos pendentes (não só a soma) —
        para exibir cada um individualmente no relatório, além do
        total agregado."""
        return self.session.query(self.model).filter(
            self.model.status == "pending"
        ).order_by(self.model.start_period.asc())
