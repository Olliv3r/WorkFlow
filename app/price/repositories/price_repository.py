from app.common.repositories.common_repository import CommonRepository
from app.models import Price


class PriceRepository(CommonRepository):
    model = Price

    def find_by_product_stage(self, product_id, stage_id):
        return self.session.query(self.model).filter(
            self.model.product_id == product_id,
            self.model.stage_id == stage_id,
        ).first()

    def list_with_relations(self):
        """Usado pela tela de cadastro/consulta — junta produto e
        etapa numa única query em vez de N+1 (um SELECT extra por
        linha ao acessar price.product/price.stage no template)."""
        from app.models import Product, Stage
        return self.session.query(self.model).join(
            Product, self.model.product_id == Product.id
        ).join(
            Stage, self.model.stage_id == Stage.id
        ).order_by(Product.id, Stage.id).all()
