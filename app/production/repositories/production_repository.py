from app.extensions import db
from sqlalchemy import func
from app.common.repositories.common_repository import CommonRepository
from app.models import Production


class ProductionRepository(CommonRepository):
    model = Production
    
    def get_unpaid_summary(self):
        return self.session.query(
            func.sum(self.model.dozens).label("total_dozens"),
            func.sum(self.model.total_amount).label("total_amount"),
        ).filter(self.model.payment_id.is_(None))

    def get_unpaid(self):
        return self.session.query(
            func.min(self.model.date).label("start_period"),
            func.max(self.model.date).label("end_period"),
        ).filter(self.model.payment_id.is_(None))
