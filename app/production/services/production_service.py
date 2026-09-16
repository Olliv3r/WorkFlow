from app.production.repositories import *
from app.stage.repositories import stage_repository
from app.production.utils.serializers import serialize_production
from app.production.mappers.production_mapper import ProductionMapper
from datetime import datetime
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.models import Production
from app.price.services.price_service import PriceService

class ProductionService:
    @staticmethod
    def get_products():
        return product_repository.filter_by(active=True).order_by(product_repository.model.id.desc()).all()
    
    @staticmethod
    def get_stages():
        return stage_repository.filter_by(active=True).order_by(stage_repository.model.order.asc()).all()

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
    def get_productions(start_date=None, end_date=None, product_id=None):
        return production_repository.filter_productions(
            start_date=start_date, end_date=end_date, product_id=product_id
        ).all()

    @staticmethod
    def get_payments():
        return payment_repository.all()

    @staticmethod
    def get_total_summary(start_date=None, end_date=None, product_id=None):
        return production_repository.get_total_summary(
            start_date=start_date, end_date=end_date, product_id=product_id
        ).first()

    @staticmethod
    def get_unpaid_summary(start_date=None, end_date=None, product_id=None):
        return production_repository.get_unpaid_summary(
            start_date=start_date, end_date=end_date, product_id=product_id
        ).first()

    @staticmethod
    def production_create(dto):
        if not dto.is_valid() or dto.date is None:
            raise ValidationError("Dados faltando ou inválidos")
        if dto.dozens <= 0:
            raise ValidationError("Quantidade de dúzias deve ser maior que zero")
        if dto.price_per_dozen <= 0:
            raise ValidationError("Preço por dúzia deve ser maior que zero")

        product = product_repository.filter_by(
            id=dto.product_id
        ).first()

        if not product:
            raise NotFoundError("Produto não foi encontrado")
        if not product.active:
            raise ValidationError("Produto está inativo")

        stage = stage_repository.filter_by(id=dto.stage_id).first()

        if not stage:
            raise NotFoundError("Não existe etapa para este produto")
        if not stage.active:
            raise ValidationError("Etapa está inativa")
      
        # A interface já trata o preço cadastrado em Price como o valor
        # vigente da combinação produto+etapa. Repetimos essa decisão no
        # backend para que um POST manual não consiga sobrescrever um preço
        # configurado apenas alterando o formulário. Se não houver preço
        # cadastrado, preservamos o fallback manual já existente no sistema.
        configured_price = PriceService.get_current_price(dto.product_id, dto.stage_id)
        price_per_dozen = configured_price if configured_price is not None else dto.price_per_dozen

        total_amount = dto.dozens * price_per_dozen
        production = Production(
            date=dto.date,
            total_amount=total_amount,
            price_per_dozen=price_per_dozen,
            observation=dto.observation,
            dozens=dto.dozens,
            product=product,
            stage=stage
        )

        production_repository.add(production)
        production_repository.commit()

        return True

    @staticmethod
    def get_production(production_id: int):
        production = production_repository.filter_by(id=production_id).first()

        if production is None:
            raise NotFoundError("Produção não encontrada")

        return production

    @staticmethod
    def get_data(production_id: int):
        production = ProductionService.get_production(production_id)
        return serialize_production(production)


    @staticmethod
    def edit(production_id: int, dto) -> bool:
        production = production_repository.filter_by(
            id=production_id
        ).first()

        if production is None:
            raise NotFoundError("Produção não encontrada")

        # Payment armazena totais congelados calculados a partir das
        # produções no momento do fechamento. Alterar uma Production já
        # vinculada sem recalcular o Payment deixaria os dois registros
        # inconsistentes. Assim como na exclusão, é necessário primeiro
        # desfazer/excluir o pagamento pendente e só então editar.
        if production.payment_id is not None:
            raise PermissionError(
                "Não é possível editar uma produção já vinculada a um pagamento"
            )

        if not dto.is_valid() or dto.date is None:
            raise ValidationError("Dados faltando ou inválidos")
        if dto.dozens <= 0:
            raise ValidationError("Quantidade de dúzias deve ser maior que zero")
        if dto.price_per_dozen <= 0:
            raise ValidationError("Preço por dúzia deve ser maior que zero")

        product = product_repository.filter_by(
            id=dto.product_id
        ).first()

        if product is None:
            raise NotFoundError("Produto não encontrado para essa produção")
        if not product.active:
            raise ValidationError("Produto está inativo")

        stage = stage_repository.filter_by(
            id=dto.stage_id
        ).first()

        if stage is None:
            raise NotFoundError("Etapa não encontrada para essa produção")
        if not stage.active:
            raise ValidationError("Etapa está inativa")

        production = ProductionMapper.to_entity(production, dto)

        production.product = product
        production.stage = stage
        production.total_amount = dto.dozens * dto.price_per_dozen

        production_repository.commit()
      
        return True

    # Excluir produção
    @staticmethod
    def production_delete(production_id: int) -> bool:
        production = production_repository.filter_by(id=production_id).first()

        if production is None:
            raise NotFoundError("Produção não encontrada")

        if production.payment_id is not None:
            raise PermissionError(
                "Não é possível excluir uma produção já vinculada a um pagamento"
            )

        production_repository.delete(production)
        production_repository.commit()

        return True

