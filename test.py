from app.production.dtos.production_dto import ProductionCreateDTO
from datetime import date
from decimal import Decimal

dto = ProductionCreateDTO.from_form(
    product_id=1,
    stage_id=1,
    dozens=2,
    price_per_dozen=Decimal("2.2"),
    date=date.today()
)

print("Tipos: ")
for attr, value in dto.__dict__.items():
  print("Attr: ",attr, ", Tipo: ",type(value))
  
print("DTO: ",dto)
print("Dados válidos?: ",dto.is_valid())
