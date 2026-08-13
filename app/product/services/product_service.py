from app.models import Product
from datetime import datetime
from app.product.repositories import product_repository
from app.core.exceptions import NotFoundError
from app.product.utils.serializers import serialize_product

class ProductService:
    @staticmethod
    def get_products():
        products = product_repository.all(order_by="id")

        if products is None:
            raise NotFoundError("Nenhum produto encontrado")

        serializeds = [serialize_product(product) for product in products]

        return serializeds