from flask import Flask, jsonify
from config import Config

from app.extensions import *

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Inicializar extensões
    db.init_app(app)
    bootstrap.init_app(app)

    from app.core.exceptions import AppException

    @app.errorhandler(AppException)
    def handle_app_exception(error):
        # O frontend atual decide sucesso/erro pelo campo `status`.
        # Mantemos HTTP 200 por compatibilidade com os módulos jQuery
        # existentes, mas expomos o código semântico em http_status.
        db.session.rollback()
        return jsonify(
            status="error",
            message=error.message,
            http_status=error.status_code,
        )

    @app.context_processor
    def database_context():
        backend = db.engine.url.get_backend_name()
        names = {
            "sqlite": "SQLite",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mariadb": "MariaDB",
        }
        return {
            "database_backend": backend,
            "database_backend_name": names.get(backend, backend.title()),
            "direct_database_backup": backend == "sqlite",
        }

    from app.models import (
            ProductFamily, Hole, Material, Payment, Product, Production, Quality, Stage, StickType, Price, DailyWork, Advance, AdvanceDeduction
    )

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.stage import bp as stage_bp
    app.register_blueprint(stage_bp, url_prefix="/stage")
  
    from app.hole import bp as hole_bp
    app.register_blueprint(hole_bp, url_prefix="/hole")
  
    from app.production import bp as production_bp
    app.register_blueprint(production_bp, url_prefix="/production")

    from app.product import bp as product_bp
    app.register_blueprint(product_bp, url_prefix="/product")

    from app.payment import bp as payment_bp
    app.register_blueprint(payment_bp, url_prefix="/payment")


    from app.daily_work import bp as daily_work_bp
    app.register_blueprint(daily_work_bp, url_prefix="/daily-work")

    from app.advance import bp as advance_bp
    app.register_blueprint(advance_bp, url_prefix="/advance")

    from app.registry import bp as registry_bp
    app.register_blueprint(registry_bp, url_prefix="/registry")

    from app.report import bp as report_bp
    app.register_blueprint(report_bp, url_prefix="/report")

    from app.price import bp as price_bp
    app.register_blueprint(price_bp, url_prefix="/price")

    return app
    
