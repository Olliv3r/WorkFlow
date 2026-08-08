from dataclasses import dataclass

class CreateBaseDTO: 
    @classmethod
    def from_form(cls, **kwargs):
        return cls(**kwargs)

    def is_valid(self):
        for attr, value in self.__dict__.items():
            #value = getattr(self, attr, "")
            if attr == "observation":
                continue

            if value is None:
                return False

            if isinstance(value, str):
                if value.strip() == "":
                    return False

            elif isinstance(value, int):
                pass

            else:
                return False

        return True

@dataclass
class CreateDTO(CreateBaseDTO):
    product_id: int
    stage_id: int
    dozens: int
    price_per_dozen: float
    date: str
    observation: str = None
