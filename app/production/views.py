from app.production import bp
from flask import render_template, request, url_for, jsonify
from app.production.services.production_service import ProductionService as ps
from app.production.dtos.production_dto import ProductionCreateDTO
from app.core.exceptions import NotFoundError, ValidationError
from datetime import date
from decimal import Decimal

@bp.route("/", methods=["GET",])
def index():
    products = ps.get_products()
    stages = ps.get_stages()
    families = ps.get_families()
    materials = ps.get_materials()
    holes = ps.get_holes()
    sticks = ps.get_sticks()
    qualities = ps.get_qualities()

    return render_template(
        "production/production_form.html",
        title="Cadastrar produções e produtos",
        products=products,
        stages=stages,
        families=families,
        materials=materials,
        holes=holes,
        sticks=sticks,
        qualities=qualities
    )

@bp.route("/create", methods=["POST"])
def create():
    form = request.form
    price_per_dozen = Decimal(form["price_per_dozen"])
    date_format = date.fromisoformat(form["date"])
  
    dto = ProductionCreateDTO.from_form(
        product_id=int(form["product_id"]),
        stage_id=int(form["stage_id"]),
        dozens=int(form["dozens"]),
        price_per_dozen=price_per_dozen,
        date=date_format,
        observation=str(form["observation"])
    )

    try:
        result = ps.production_create(dto)
        if not result:
            return jsonify(
                status="error", 
                message="Não foi possível registrar a produção"
            )

        return jsonify(
            status="success",
            message="Produção registrada com sucesso"
        )

    except (NotFoundError, ValidationError) as error:
        return jsonify(status="error", message=str(error.message))

