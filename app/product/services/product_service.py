from app.models import Product
from datetime import datetime
from app.product.repositories import product_repository
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.product.utils.serializers import serialize_product

# Repositórios de entidades relacionadas — mesmos usados em
# production_service.py para validar existência de família, material,
# furo e taco antes de criar. Importados dos módulos individuais (não
# de app.production.repositories, o __init__ agregador) porque esse
# pacote já importa de volta app.product.repositories — importar o
# agregador aqui criaria um ciclo que hoje só não quebra por sorte de
# ordem de carregamento.
from app.production.repositories.family_repository import FamilyRepository
from app.production.repositories.material_repository import MaterialRepository
from app.production.repositories.hole_repository import HoleRepository
from app.production.repositories.stick_repository import StickRepository
from app.production.repositories.quality_repository import QualityRepository

family_repository = FamilyRepository()
material_repository = MaterialRepository()
hole_repository = HoleRepository()
stick_repository = StickRepository()
quality_repository = QualityRepository()


class ProductService:
    @staticmethod
    def get_products():
        products = product_repository.all(order_by="id")

        if products is None:
            raise NotFoundError("Nenhum produto encontrado")

        serializeds = [serialize_product(product) for product in products]

        return serializeds



    @staticmethod
    def get_form_options():
        return {
            "families": family_repository.all(order_by="name"),
            "materials": material_repository.all(order_by="name"),
            "holes": hole_repository.all(order_by="quantity"),
            "sticks": stick_repository.all(order_by="name"),
            "qualities": quality_repository.all(order_by="name"),
        }

    @staticmethod
    def get_product_entities():
        return product_repository.all(order_by="id", descending=True)

    @staticmethod
    def toggle_active(product_id: int):
        product = product_repository.filter_by(id=product_id).first()
        if product is None:
            raise NotFoundError("Produto não encontrado")
        product.active = not product.active
        product_repository.commit()
        return product

    @staticmethod
    def create(dto):
        if not dto.is_valid():
            raise ValidationError("Dados faltando")

        family = family_repository.filter_by(id=dto.family_id).first()
        if not family:
            raise NotFoundError("Família não encontrada")

        material = material_repository.filter_by(id=dto.material_id).first()
        if not material:
            raise NotFoundError("Material não encontrado")

        hole = hole_repository.filter_by(id=dto.hole_id).first()
        if not hole:
            raise NotFoundError("Quantidade de furos não encontrada")

        stick_type = stick_repository.filter_by(id=dto.stick_type_id).first()
        if not stick_type:
            raise NotFoundError("Tipo de taco não encontrado")

        quality = None
        if dto.quality_id is not None:
            quality = quality_repository.filter_by(id=dto.quality_id).first()
            if not quality:
                raise NotFoundError("Qualidade não encontrada")

        # Um produto é a combinação destes 5 atributos — duas linhas
        # idênticas não são produtos diferentes, são a mesma coisa
        # duas vezes (decisão registrada: bloquear duplicata).
        duplicate = product_repository.find_duplicate(
            family_id=dto.family_id,
            material_id=dto.material_id,
            hole_id=dto.hole_id,
            stick_type_id=dto.stick_type_id,
            quality_id=dto.quality_id,
        )
        if duplicate is not None:
            raise ConflictError(
                "Já existe um produto com esta mesma combinação de "
                "família, material, furos, taco e qualidade"
            )

        product = Product(
            family=family,
            material=material,
            hole=hole,
            stick_type=stick_type,
            quality=quality,
        )

        product_repository.add(product)
        product_repository.commit()

        return product