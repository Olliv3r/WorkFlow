# EXTERNOS
from app.production.repositories.production_repository import ProductionRepository

# ROOT
from .payment_repository import PaymentRepository

# INSTANCIAS
payment_repository = PaymentRepository()
production_repository = ProductionRepository()