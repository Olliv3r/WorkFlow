from app.models import Production

def serialize_production(production: Production) -> dict:
    return {
        "id": production.id,
        "dozens": production.dozens,
        "price_per_dozen": production.price_per_dozen,
        "total_amount": production.total_amount,
        "observation": production.observation,
        "product_id": production.product_id,
        "stage_id": production.stage_id,
        "payment_id": production.payment_id,
        "entity": "production"
    }