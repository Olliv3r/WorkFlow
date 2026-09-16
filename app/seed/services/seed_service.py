from app.models import *
from app.seed.seed_dict import *
from app.production.repositories import *
from app.stage.repositories import stage_repository
from app.price.repositories import price_repository

class SeedService:
    @staticmethod
    def create_entity(list_dict: list, repository, model, identity_field="name"):
        for item in list_dict:
            identity = {identity_field: item[identity_field]}
            entity_existing = repository.filter_by(**identity).first()

            if entity_existing:
                for key, value in item.items():
                    setattr(entity_existing, key, value)
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
            Hole,
            identity_field="quantity"
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

        # EXTRA 22/30 inherit the real EXTRA 20 combination instead of
        # duplicating assumptions about material, quality or stick type.
        extra_family = family_repository.filter_by(name="Extra").first()
        hole20 = hole_repository.filter_by(quantity=20).first()
        if extra_family and hole20:
            source = product_repository.filter_by(family=extra_family, hole=hole20).first()
            if source:
                for quantity in (22, 30):
                    target_hole = hole_repository.filter_by(quantity=quantity).first()
                    if target_hole is None:
                        raise ValueError(f"Furos {quantity} não encontrados")
                    existing = product_repository.filter_by(
                        family=source.family, material=source.material, quality=source.quality,
                        hole=target_hole, stick_type=source.stick_type).first()
                    if not existing:
                        existing = Product(family=source.family, material=source.material, quality=source.quality,
                            hole=target_hole, stick_type=source.stick_type)
                        product_repository.add(existing)
                        product_repository.session.flush()
                    source_prices = price_repository.filter_by(product_id=source.id).all()
                    for source_price in source_prices:
                        price_exists = price_repository.filter_by(product_id=existing.id, stage_id=source_price.stage_id).first()
                        if not price_exists:
                            price_repository.add(Price(product_id=existing.id, stage_id=source_price.stage_id,
                                price_per_dozen=source_price.price_per_dozen))

        return product_repository.commit()

    
