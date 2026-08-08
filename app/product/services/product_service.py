from app.product.repositories.product_repository import ProductRepository
from app.models import Product
from datetime import datetime

product_repository = ProductRepository()

class ProductService:
    @staticmethod
    def product_create(dto):
        pass
