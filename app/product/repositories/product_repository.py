from app.common.repositories.common_repository import CommonRepository
from app.models import Product


class ProductRepository(CommonRepository):
    model = Product

    def find_duplicate(self, family_id, material_id, hole_id, stick_type_id, quality_id=None):
        """
        Um produto é a combinação de atributos físicos — duas linhas
        idênticas não representam produtos diferentes, representam a
        mesma coisa duas vezes. quality_id é opcional (Optional[int]
        no model), então is_(None) é necessário quando ausente —
        == None não funciona de forma confiável em todos os dialetos
        SQL para comparar NULL.
        """
        query = self.session.query(self.model).filter(
            self.model.family_id == family_id,
            self.model.material_id == material_id,
            self.model.hole_id == hole_id,
            self.model.stick_type_id == stick_type_id,
        )
        if quality_id is None:
            query = query.filter(self.model.quality_id.is_(None))
        else:
            query = query.filter(self.model.quality_id == quality_id)
        return query.first()