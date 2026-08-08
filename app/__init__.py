from flask import Flask
from config import Config

from app.extensions import *

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializar extensões
    db.init_app(app)
    bootstrap.init_app(app)

    from app.models import (
            ProductFamily, Hole, Material, Payment, Product, Production, Quality, Stage, StickType
    )

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.production import bp as production_bp
    app.register_blueprint(production_bp, url_prefix="/production")

    from app.product import bp as product_bp
    app.register_blueprint(product_bp, url_prefix="/product")

    from app.payment import bp as payment_bp
    app.register_blueprint(payment_bp, url_prefix="/payment")

    return app
    
