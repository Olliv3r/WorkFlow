from app.models import Stage

def serialize_stage(stage: Stage) -> dict:
    return {"id": stage.id, "name": stage.name, "entity": "stage"}