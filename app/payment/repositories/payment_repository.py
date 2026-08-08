from app.extensions import db
from app.common.repositories.common_repository import CommonRepository
from app.models import Payment

class PaymentRepository(CommonRepository):
    model = Payment