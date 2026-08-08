from dataclasses import dataclass
from datetime import date
from decimal import Decimal

class CreateBaseDTO: 
    @classmethod
    def from_form(cls, **kwargs):
        return cls(**kwargs)

@dataclass
class ProductionCreateDTO(CreateBaseDTO):
    product_id: int
    stage_id: int
    dozens: int
    price_per_dozen: Decimal
    date: date
    observation: str | None = None

    def is_valid(self):
        return (
            isinstance(self.product_id, int) and isinstance(self.stage_id, int) and isinstance(self.dozens, int) and isinstance(self.price_per_dozen, Decimal) and isinstance(self.date, date) and (
    self.observation is None or
    isinstance(self.observation, str)
            )
        )
