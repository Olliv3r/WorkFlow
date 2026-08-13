from app.models import Product

def serialize_product(product: Product) -> dict:
    return {
        "id": product.id,
        "family_name": product.family.name,
        "material_name": product.material.name,
        "hole_quantity": product.hole.quantity,
        # "quality_name": product.quality.name,
        # "quantity": product.quality.name,
        # "stick": product.stick_type.name
    }