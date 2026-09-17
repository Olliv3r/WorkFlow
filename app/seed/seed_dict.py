PRODUCT_FAMILIES = [
    {
        "name": "Básica",
        "description": "Vassoura menor, taco de 16 furos, material padrão/inferior."
    },
    {
        "name": "Extra",
        "description": "Linha padrão, taco lixado, 20 furos e piaçaba de boa qualidade."
    },
    {
        "name": "Inovada",
        "description": "Linha premium com design diferenciado e melhor material."
    },
    {
        "name": "Capa Quadrada",
        "description": "Taco plástico resistente e piaçaba de alta qualidade."
    },
    {
        "name": "PET",
        "description": "Linha baseada em material PET com variações de furos."
    },
    {
        "name": "Nailon",
        "description": "Linha baseada em material nailon."
    },
    {
        "name": "Cipó",
        "description": "Linha baseada em material cipó."
    }
]
MATERIALS = [
    {
        "name": "Piaçaba",
        "description": "Fibra natural utilizada nas linhas principais."
    },
    {
        "name": "PET",
        "description": "Material proveniente de garrafas PET."
    },
    {
        "name": "Nailon",
        "description": "Fibra sintética de nailon."
    },
    {
        "name": "Cipó",
        "description": "Fibra natural de cipó."
    }
]
HOLES = [
    {
        "quantity": 16
    },
    {
        "quantity": 20
    },
    {
        "quantity": 22
    }
]
PIACABA_QUALITIES = [
    {
        "name": "Média",
        "description": "Material intermediário."
    },
    {
        "name": "Boa",
        "description": "Material de melhor qualidade."
    },
    {
        "name": "Premium",
        "description": "Melhor qualidade disponível."
    }
]
STICK_TYPES = [
    {
        "name": "Taco padrão",
        "description": "Modelo tradicional."
    },
    {
        "name": "Taco padrão lixado",
        "description": "Taco com acabamento melhor nas bordas."
    },
    {
        "name": "Taco especial",
        "description": "Design diferenciado da linha Inovada."
    },
    {
        "name": "Taco plástico",
        "description": "Taco utilizado na Capa Quadrada."
    },
    {
        "name": "Taco simples",
        "description": "Taco utilizado na linha Nailon."
    }
]
STAGES = [
    {"name": "Amarração", "order": 1},
    {"name": "Enchimento", "order": 2},
]
PRODUCTS = [
    {"family":"Básica","material":"Piaçaba","quality":"Média","hole":16,"stick_type":"Taco padrão"},
    {"family":"Extra","material":"Piaçaba","quality":"Boa","hole":16,"stick_type":"Taco padrão lixado"},
    {"family":"Extra","material":"Piaçaba","quality":"Boa","hole":20,"stick_type":"Taco padrão lixado"},
    {"family":"Extra","material":"Piaçaba","quality":"Boa","hole":22,"stick_type":"Taco padrão lixado"},
    {"family":"Inovada","material":"Piaçaba","quality":"Premium","hole":20,"stick_type":"Taco especial"},
    {"family":"Capa Quadrada","material":"Piaçaba","quality":"Premium","hole":None,"stick_type":"Taco plástico"},
    {"family":"PET","material":"PET","quality":None,"hole":16,"stick_type":"Taco padrão"},
    {"family":"PET","material":"PET","quality":None,"hole":20,"stick_type":"Taco padrão"},
    {"family":"Nailon","material":"Nailon","quality":None,"hole":16,"stick_type":"Taco simples"},
    {"family":"Nailon","material":"Nailon","quality":None,"hole":20,"stick_type":"Taco simples"},
    {"family":"Cipó","material":"Cipó","quality":None,"hole":16,"stick_type":"Taco padrão"},
    {"family":"Cipó","material":"Cipó","quality":None,"hole":20,"stick_type":"Taco padrão"},
]

# Current price per dozen. Both production stages share the same price,
# except Capa Quadrada. Historical Production.price_per_dozen is untouched.
DEFAULT_PRICES = {
    ("Básica", 16): {"Amarração": "2.00", "Enchimento": "2.00"},
    ("Extra", 16): {"Amarração": "2.00", "Enchimento": "2.00"},
    ("Extra", 20): {"Amarração": "2.50", "Enchimento": "2.50"},
    ("Extra", 22): {"Amarração": "3.00", "Enchimento": "3.00"},
    ("Inovada", 20): {"Amarração": "2.50", "Enchimento": "2.50"},
    ("PET", 16): {"Amarração": "4.00", "Enchimento": "4.00"},
    ("PET", 20): {"Amarração": "5.00", "Enchimento": "5.00"},
    ("Nailon", 16): {"Amarração": "2.00", "Enchimento": "2.00"},
    ("Nailon", 20): {"Amarração": "2.50", "Enchimento": "2.50"},
    ("Cipó", 16): {"Amarração": "2.50", "Enchimento": "2.50"},
    ("Cipó", 20): {"Amarração": "3.00", "Enchimento": "3.00"},
    ("Capa Quadrada", None): {"Amarração": "1.50", "Enchimento": "2.50"},
}
