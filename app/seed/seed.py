from app.seed.services.seed_service import SeedService

print("Populando dados padrão...")
sd = SeedService()

steps = [
    ("Famílias de produtos", sd.create_product_families),
    ("Materiais", sd.create_materials),
    ("Qualidades (piaçaba)", sd.create_qualities),
    ("Furos", sd.create_holes),
    ("Tipos de taco", sd.create_stick_types),
    ("Etapas", sd.create_stages),
    ("Produtos", sd.create_products),
]
for label, action in steps:
    print(f"- {label}...")
    action()
    print("  OK")

print("- Preços...")
created_prices = sd.create_prices()
print(f"  OK ({created_prices} preço(s) novo(s) cadastrado(s); existentes preservados)")
print("Seed concluído.")
