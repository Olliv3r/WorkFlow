
class ProductionMapper:
    @staticmethod
    def to_entity(production, dto):
        production.dozens = dto.dozens
        production.price_per_dozen = dto.price_per_dozen
        production.observation = dto.observation

        return production