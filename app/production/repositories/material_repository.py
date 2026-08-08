from app.common.repositories.common_repository import CommonRepository
from app.models import Material

class MaterialRepository(CommonRepository):
    model = Material