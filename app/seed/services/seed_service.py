from app.models import *
from app.seed.seed_dict import *
from app.production.repositories import *

class SeedService:
    @staticmethod
    def create_entity(list_dict: list, repository, model):
        for item in list_dict:
            entity_existing = repository.filter_by(**item).first()

            if entity_existing:
                continue

            entity_new = model(**item)

            repository.add(entity_new)
        return repository.commit()

    @staticmethod
    def create_product_families():
        return SeedService.create_entity(
            PRODUCT_FAMILIES,
            family_repository,
            ProductFamily
        )

    @staticmethod
    def create_materials():
        return SeedService.create_entity(
            MATERIALS,
            material_repository,
            Material
        )

    @staticmethod
    def create_qualities():
        return SeedService.create_entity(
            PIACABA_QUALITIES,
            quality_repository,
            Quality
        )


    @staticmethod
    def create_holes():
        return SeedService.create_entity(
            HOLES,
            hole_repository,
            Hole
        )


    @staticmethod
    def create_stick_types():
        return SeedService.create_entity(
            STICK_TYPES,
            stick_repository,
            StickType
        )
 

    @staticmethod
    def create_stages():
        return SeedService.create_entity(
            STAGES,
            stage_repository,
            Stage
        )


    @staticmethod
    def create_products():
        for item in PRODUCTS:
            family = family_repository.filter_by(
                name=item['family']
            ).first()

            if family is None:
                raise ValueError("A família do produto não foi encontrada")

            material = material_repository.filter_by(
                name=item['material']
            ).first()

            if material is None:
                raise ValueError("O material do produto não foi encontrado")

            quality = quality_repository.filter_by(
                name=item['quality']
            ).first()

            hole = hole_repository.filter_by(
                quantity=item['hole']
            ).first()

            if hole is None:
                raise ValueError("Os furos do produto não foi encontrado")

            stick_type = stick_repository.filter_by(
                name=item['stick_type']
            ).first() 

            if stick_type is None:
                raise ValueError('Os tipos de tacos do produto não existem')

            product_existing = product_repository.filter_by(
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

            product_repository.add(product_new)

        return product_repository.commit()

    
