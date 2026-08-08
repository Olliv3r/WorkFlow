from app.common.repositories.common_repository import CommonRepository
from app.models import Product

class ProductRepository(CommonRepository):
    model = Product