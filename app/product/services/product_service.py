from app.product.repositories.product_repository import ProductRepository as Repository
from app.models import Product
from datetime import datetime

product_repository = Repository(Product)

class ProductService:
    @staticmethod
    def product_create(dto):
        pass
