"""
NOTA: app/product/dtos/dto.py já existe, mas contém CreateDTO com
campos de Produção (product_id, stage_id, dozens...), não de Produto
— parece copiado do DTO de produção por engano, e nunca foi usado
para criar produto (product_service.py nunca o importa). Não editei
aquele arquivo por estar fora do escopo desta tarefa; este arquivo
novo é o DTO correto para criação de produto.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


class CreateBaseDTO:
    @classmethod
    def from_form(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class ProductCreateDTO(CreateBaseDTO):
    family_id: int
    material_id: int
    hole_id: Optional[int]
    stick_type_id: int
    quality_id: Optional[int] = None

    def is_valid(self) -> bool:
        return (
            isinstance(self.family_id, int)
            and isinstance(self.material_id, int)
            and (self.hole_id is None or isinstance(self.hole_id, int))
            and isinstance(self.stick_type_id, int)
            and (self.quality_id is None or isinstance(self.quality_id, int))
        )
