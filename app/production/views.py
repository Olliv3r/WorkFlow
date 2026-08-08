from app.production import bp
from flask import render_template, request, url_for, jsonify
from app.production.services.production_service import ProductionService as ps
from app.production.dtos.dto import CreateDTO
from app.core.exceptions import NotFoundError, ValidationError

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
    dto = CreateDTO.from_form(
        product_id=request.form.get("product_id"),
        stage_id=request.form.get("stage_id"),
        dozens=request.form.get("dozens"),
        price_per_dozen=request.form.get("price_per_dozen"),
        date=request.form.get("date"),
        observation=request.form.get("observation")
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

