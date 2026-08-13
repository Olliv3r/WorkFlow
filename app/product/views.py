from app.product import bp
from flask import jsonify
from app.product.services.product_service import ProductService as ps
from app.core.exceptions import NotFoundError

@bp.route("/options", methods=["GET"])
def get_options():
    try:
        products = ps.get_products()
        return jsonify(status="success", message="Dados de produtos encontrados", products=products)
      
    except NotFoundError as error:
        return jsonify(status="error", message=str(error.message))