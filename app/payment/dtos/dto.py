from dataclasses import dataclass

class PaymentCreateBaseDTO: 
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
class PaymentCreateDTO(PaymentCreateBaseDTO):
    production_ids: list[int]
    #period: str = None
    #payment_date: date
    observation: str = None
