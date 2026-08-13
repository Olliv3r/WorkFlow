# EXTERNO
from app.product.repositories.product_repository import ProductRepository
from app.payment.repositories.payment_repository import PaymentRepository

# ROOT
from .production_repository import ProductionRepository
from .family_repository import FamilyRepository
from .material_repository import MaterialRepository
from .hole_repository import HoleRepository
from .stick_repository import StickRepository
from .quality_repository import QualityRepository

# INSTANCIAS
product_repository = ProductRepository()
family_repository = FamilyRepository()
material_repository = MaterialRepository()
hole_repository = HoleRepository()
stick_repository = StickRepository()
quality_repository = QualityRepository()
production_repository = ProductionRepository()
payment_repository = PaymentRepository()