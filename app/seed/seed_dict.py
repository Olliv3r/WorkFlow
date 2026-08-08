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
        "quantity": 30
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
    {
        "name": "Amarração",
        "order": 1
    },
    {
        "name": "Enchimento",
        "order": 2
    },
    {
        "name": "Pinação",
        "order": 3
    },
    {
        "name": "Pentiação",
        "order": 4
    },
    {
        "name": "Aparação",
        "order": 5
    },
    {
        "name": "Encabação",
        "order": 6
    },
    {
        "name": "Pinação do cabo",
        "order": 7
    },
    {
        "name": "Acabamento",
        "order": 8
    }
]
PRODUCTS = [

    # ==========================
    # BÁSICA
    # ==========================

    {
        "family": "Básica",
        "material": "Piaçaba",
        "quality": "Média",
        "hole": 16,
        "stick_type": "Taco padrão"
    },


    # ==========================
    # EXTRA
    # ==========================

    {
        "family": "Extra",
        "material": "Piaçaba",
        "quality": "Boa",
        "hole": 20,
        "stick_type": "Taco padrão lixado"
    },


    # ==========================
    # INOVADA
    # ==========================

    {
        "family": "Inovada",
        "material": "Piaçaba",
        "quality": "Premium",
        "hole": 20,
        "stick_type": "Taco especial"
    },


    # ==========================
    # CAPA QUADRADA
    # ==========================

    {
        "family": "Capa Quadrada",
        "material": "Piaçaba",
        "quality": "Premium",
        "hole": 20,
        "stick_type": "Taco plástico"
    },


    # ==========================
    # PET
    # ==========================

    {
        "family": "PET",
        "material": "PET",
        "quality": None,
        "hole": 16,
        "stick_type": "Taco padrão"
    },

    {
        "family": "PET",
        "material": "PET",
        "quality": None,
        "hole": 20,
        "stick_type": "Taco padrão"
    },

    {
        "family": "PET",
        "material": "PET",
        "quality": None,
        "hole": 30,
        "stick_type": "Taco padrão"
    },


    # ==========================
    # NAILON
    # ==========================

    {
        "family": "Nailon",
        "material": "Nailon",
        "quality": None,
        "hole": 16,
        "stick_type": "Taco simples"
    },

    {
        "family": "Nailon",
        "material": "Nailon",
        "quality": None,
        "hole": 20,
        "stick_type": "Taco simples"
    },

    {
        "family": "Nailon",
        "material": "Nailon",
        "quality": None,
        "hole": 30,
        "stick_type": "Taco simples"
    },


    # ==========================
    # CIPÓ
    # ==========================

    {
        "family": "Cipó",
        "material": "Cipó",
        "quality": None,
        "hole": 16,
        "stick_type": "Taco padrão"
    },

    {
        "family": "Cipó",
        "material": "Cipó",
        "quality": None,
        "hole": 20,
        "stick_type": "Taco padrão"
    },

    {
        "family": "Cipó",
        "material": "Cipó",
        "quality": None,
        "hole": 30,
        "stick_type": "Taco padrão"
    },

]

