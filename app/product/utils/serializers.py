def serialize_product(product):
    hole_quantity = product.hole.quantity if product.hole else None
    hole_label = f" - {hole_quantity} furos" if hole_quantity is not None else " - sem furos"
    return {
        "id": product.id,
        "family_name": product.family.name,
        "material_name": product.material.name,
        "quality_name": product.quality.name if product.quality else None,
        "hole_quantity": hole_quantity,
        "stick_type_name": product.stick_type.name,
        "display_name": f"{product.family.name} - {product.material.name}{hole_label}",
        "active": product.active,
    }
