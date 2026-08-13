from app.hole.utils.serializers import serialize_hole
from app.core.exceptions import NotFoundError
from app.hole.repositories import hole_repository

class HoleService:
    @staticmethod
    def get_holes():
        holes = hole_repository.all(order_by="id")

        if holes is None:
            raise NotFoundError("Nenhuma quantida de furos encontrada")

        serializeds = [
            serialize_hole(hole) for hole in holes
        ]

        return serializeds