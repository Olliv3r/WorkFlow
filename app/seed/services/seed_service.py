from app.seed.repositories.seed_repository import SeedRepository
from app.models import *
from app.seed.seed_dict import *

repository = SeedRepository()

class SeedService:
    @staticmethod
    def create_entity(list_dict: list, model):
        for item in list_dict:
            entity_existing = repository.select(model).filter_by(**item).first()

            if entity_existing:
                continue

            entity_new = model(**item)

            repository.add(entity_new)
        return repository.commit()

    @staticmethod
    def create_product_families():
        return SeedService.create_entity(
            PRODUCT_FAMILIES,
            ProductFamily
        )

    @staticmethod
    def create_materials():
        return SeedService.create_entity(
            MATERIALS,
            Material
        )

    @staticmethod
    def create_qualities():
        return SeedService.create_entity(
            PIACABA_QUALITIES,
            Quality
        )


    @staticmethod
    def create_holes():
        return SeedService.create_entity(
            HOLES,
            Hole
        )


    @staticmethod
    def create_stick_types():
        return SeedService.create_entity(
            STICK_TYPES,
            StickType
        )
 

    @staticmethod
    def create_stages():
        return SeedService.create_entity(
            STAGES,
            Stage
        )


    @staticmethod
    def create_products():
        for item in PRODUCTS:
            family = repository.select(ProductFamily).filter_by(
                name=item['family']
            ).first()

            if family is None:
                raise ValueError("A família do produto não foi encontrada")

            material = repository.select(Material).filter_by(
                name=item['material']
            ).first()

            if material is None:
                raise ValueError("O material do produto não foi encontrado")

            quality = repository.select(Quality).filter_by(
                name=item['quality']
            ).first()

            hole = repository.select(Hole).filter_by(
                quantity=item['hole']
            ).first()

            if hole is None:
                raise ValueError("Os furos do produto não foi encontrado")

            stick_type = repository.select(StickType).filter_by(
                name=item['stick_type']
            ).first() 

            if stick_type is None:
                raise ValueError('Os tipos de tacos do produto não existem')

            product_existing = repository.select(Product).filter_by(
                family=family,
                material=material,
                quality=quality,
                hole=hole,
                stick_type=stick_type
            ).first()

            if product_existing:
                continue

            product_new = Product(
                family=family,
                material=material,
                quality=quality,
                hole=hole,
                stick_type=stick_type
            )

            repository.add(product_new)

        return repository.commit()

    
