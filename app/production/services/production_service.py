from app.production.repositories import *
from app.stage.repositories import stage_repository
from app.production.utils.serializers import serialize_production
from app.production.mappers.production_mapper import ProductionMapper
from datetime import datetime
from app.core.exceptions import NotFoundError, ValidationError
from app.models import Production

class ProductionService:
    @staticmethod
    def get_products():
        return product_repository.all(order_by="id", descending=True)
    
    @staticmethod
    def get_stages():
        return stage_repository.all()

    @staticmethod
    def get_families():
        return family_repository.all()

    @staticmethod
    def get_materials():
        return material_repository.all()

    @staticmethod
    def get_holes():
        return hole_repository.all()

    @staticmethod
    def get_sticks():
        return stick_repository.all()

    @staticmethod
    def get_qualities():
        return quality_repository.all()

    @staticmethod
    def get_productions():
        return production_repository.all()

    @staticmethod
    def get_payments():
        return payment_repository.all()

    @staticmethod
    def get_unpaid_summary():
        return production_repository.get_unpaid_summary().first()

    @staticmethod
    def production_create(dto):
        if not dto.is_valid():
            raise ValidationError("Dados faltando")

        product = product_repository.filter_by(
            id=dto.product_id
        ).first()

        if not product:
            raise NotFoundError("Produto não foi encontrado")

        stage = stage_repository.filter_by(id=dto.stage_id).first()

        if not stage:
            raise NotFoundError("Não existe etapa para este produto")
      
        total_amount = dto.dozens * dto.price_per_dozen
        production = Production(
            date=dto.date,
            total_amount=total_amount,
            price_per_dozen=dto.price_per_dozen,
            observation=dto.observation,
            dozens=dto.dozens,
            product=product,
            stage=stage
        )

        production_repository.add(production)
        production_repository.commit()

        return True

    @staticmethod
    def get_data(production_id: int):
        production = production_repository.filter_by(id=production_id).first()

        if production is None:
            raise NotFoundError("Produção não encontrada")

        serialized = serialize_production(production)
      
        return serialized


    @staticmethod
    def edit(production_id: int, dto) -> bool:
        production = production_repository.filter_by(
            id=production_id
        ).first()

        if production is None:
            raise NotFoundError("Produção não encontrada")

        if not dto.is_valid():
            raise ValidationError("Dados faltando")

        product = product_repository.filter_by(
            id=dto.product_id
        ).first()

        if product is None:
            raise NotFoundError("Produto não encontrado para essa produção")

        stage = stage_repository.filter_by(
            id=dto.stage_id
        ).first()

        if stage is None:
            raise NotFoundError("Etapa não encontrada para essa produção")

        production = ProductionMapper.to_entity(production, dto)

        production.product = product
        production.stage = stage
        production.total_amount = dto.dozens * dto.price_per_dozen

        production_repository.commit()
      
        return True

