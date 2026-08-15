from app.production import bp
from flask import render_template, request, url_for, jsonify
from app.production.services.production_service import ProductionService as ps
from app.production.dtos.production_dto import ProductionCreateDTO
from app.core.exceptions import NotFoundError, ValidationError
from datetime import date
from decimal import Decimal


# Página padrão
@bp.route("/", methods=["GET"])
def index():
    products = ps.get_products()
    stages = ps.get_stages()
  
    return render_template(
        "production/productions.html",
        title="Gerenciar produções",
        products=products,
        stages=stages
    )

# Partial de cards
@bp.route("/cards/partial", methods=["GET"])
def cards_partial():
    productions = ps.get_productions()
    unpaid_count, total_dozens, total_amount = ps.get_unpaid_summary()
  
    return jsonify(
        render_template(
            "production/_cards.html",
            productions=productions,
            unpaid_count=unpaid_count,
            total_dozens=total_dozens,
            total_amount=total_amount
        )
    )

# Partial de tabela
@bp.route("/table/partial", methods=["GET"])
def table_partial():
    productions = ps.get_productions()

    return jsonify(
        render_template(
            "production/_table.html",
            productions=productions
        )
    )

# Criar produção
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

# Consegue dados de produção
@bp.route("/<int:production_id>/data", methods=["GET"])
def get_data(production_id):
    try:
        production = ps.get_data(production_id)
        return jsonify(status="success", message="Dados de produção encontrados", data=production)
    
    except NotFoundError as error:
        return jsonify(status="error", message=str(error.message))

# Editar dados da produção
@bp.route("/<int:production_id>/edit", methods=["POST"])
def edit_data(production_id):
    form = request.form
    price_per_dozen = Decimal(form["price_per_dozen"])
  
    try:
        dto = ProductionCreateDTO.from_form(
            product_id=int(form["product_id"]),
            stage_id=int(form["stage_id"]),
            dozens=int(form["dozens"]),
            price_per_dozen=price_per_dozen,
            observation=str(form["observation"])
        )

        result = ps.edit(production_id, dto)

        if not result:
            return jsonify(status="error", message="Não foi possível editar os dados")

        return jsonify(status="success", message="Dados editados com sucesso")
      
    except (NotFoundError, ValidationError) as error:
        return jsonify(status="error", message=str(error.message))
      
    