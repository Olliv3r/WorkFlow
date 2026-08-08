from app.seed.services.seed_service import SeedService

print('Creating data default...')
sd = SeedService()

print("Familia de produtos...")
sd.create_product_families()
print("Materiais...")
sd.create_materials()
print("Qualidades (piaçaba)...")
sd.create_qualities()
print("Furus...")
sd.create_holes()
print("Tacos...")
sd.create_stick_types()
print("Etapas...")
sd.create_stages()
print("Produtos...")
sd.create_products()
