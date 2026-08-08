from app.product import bp
from flask import render_template, request, url_for, jsonify
from app.product.services.product_service import ProductService as ps

@bp.route("/product/create", methods=["GET", "POST"])
def product_create():
    return "Nada"

