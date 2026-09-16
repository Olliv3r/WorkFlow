from __future__ import annotations
from dataclasses import dataclass


class CreateBaseDTO:
    @classmethod
    def from_form(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class PriceSetDTO(CreateBaseDTO):
    product_id: int
    stage_id: int
    price_per_dozen: "Decimal"

    def is_valid(self) -> bool:
        from decimal import Decimal
        return (
            isinstance(self.product_id, int)
            and isinstance(self.stage_id, int)
            and isinstance(self.price_per_dozen, Decimal)
            and self.price_per_dozen > 0
        )
