from app.stage.utils.serializers import serialize_stage
from app.core.exceptions import NotFoundError
from app.stage.repositories import stage_repository

class StageService:
    @staticmethod
    def get_stages():
        stages = stage_repository.all(order_by="name")

        if stages is None:
            raise NotFoundError("Nenhuma etapa encontrada")

        serializeds = [
            serialize_stage(stage) for stage in stages
        ]

        return serializeds