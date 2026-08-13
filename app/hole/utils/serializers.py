from app.models import Hole

def serialize_hole(hole: Hole) -> dict:
    return {"id": hole.id, "quantity": hole.quantity}