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
        from decimal import Decimal
        for item in PRODUCTS:
            family = family_repository.filter_by(name=item["family"]).first()
            material = material_repository.filter_by(name=item["material"]).first()
            quality = quality_repository.filter_by(name=item["quality"]).first() if item["quality"] else None
            hole = hole_repository.filter_by(quantity=item["hole"]).first() if item["hole"] is not None else None
            stick_type = stick_repository.filter_by(name=item["stick_type"]).first()
            if not family or not material or (item["hole"] is not None and not hole) or not stick_type:
                raise ValueError(f"Cadastro base ausente para produto {item['family']}")
            query = product_repository.filter_by(family=family, material=material, quality=quality, stick_type=stick_type)
            query = query.filter(Product.hole_id == (hole.id if hole else None))
            product = query.first()
            if not product:
                product = Product(family=family, material=material, quality=quality, hole=hole, stick_type=stick_type)
                product_repository.add(product); product_repository.session.flush()
            product.active = True

        return product_repository.commit()

    @staticmethod
    def create_prices():
        """Cadastra apenas preços ausentes.

        O seed nunca sobrescreve um preço que o usuário já alterou. Produções
        históricas também continuam com price_per_dozen congelado.
        """
        from decimal import Decimal
        created = 0
        for (family_name, hole_qty), stage_prices in DEFAULT_PRICES.items():
            family = family_repository.filter_by(name=family_name).first()
            if not family:
                continue
            q = product_repository.filter_by(family=family)
            if hole_qty is None:
                q = q.filter(Product.hole_id.is_(None))
            else:
                hole = hole_repository.filter_by(quantity=hole_qty).first()
                if not hole:
                    continue
                q = q.filter(Product.hole_id == hole.id)
            product = q.first()
            if not product:
                continue
            for stage_name, value in stage_prices.items():
                stage = stage_repository.filter_by(name=stage_name).first()
                if not stage:
                    continue
                row = price_repository.filter_by(product_id=product.id, stage_id=stage.id).first()
                if row is None:
                    price_repository.add(Price(
                        product_id=product.id, stage_id=stage.id,
                        price_per_dozen=Decimal(value)
                    ))
                    created += 1
        price_repository.commit()
        return created
