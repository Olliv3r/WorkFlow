"""
BUG CORRIGIDO: sem `from __future__ import annotations`, a anotação
`date: date | None = None` quebra em runtime — o nome do campo
`date` sombreia o `datetime.date` importado, no MESMO passe de
avaliação da classe (Python resolve anotações com `X | Y` em tempo
de execução por padrão desde 3.10). O erro real era:
`TypeError: unsupported operand type(s) for |: 'NoneType' and 'NoneType'`,
reproduzido isolado antes desta correção. `from __future__ import
annotations` faz o Python tratar anotações como string (avaliação
preguiçosa), resolvendo o conflito sem precisar renomear o campo.
"""
from __future__ import annotations
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
    date: date | None = None
    observation: str | None = None

    def is_valid(self):
        return (
            isinstance(self.product_id, int)
            and isinstance(self.stage_id, int) 
            and isinstance(self.dozens, int) 
            and isinstance(self.price_per_dozen, Decimal) 
            and (
                self.date is None 
                or isinstance(self.date, date)
            ) 
            and (
                self.observation is None 
                or isinstance(self.observation, str)
            )
        )
