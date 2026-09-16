from app.price import bp
from flask import render_template, request, jsonify
from app.price.services.price_service import PriceService as ps
from app.price.dtos.price_dto import PriceSetDTO
from app.core.exceptions import NotFoundError, ValidationError
from app.stage.repositories.stage_repository import StageRepository
from decimal import Decimal, InvalidOperation

# Mesma nota de app/price/services/price_service.py: ProductRepository
# aqui é importado do módulo product diretamente, não de
# app.production.repositories (que também o re-exporta e criaria o
# mesmo risco de ciclo já resolvido em product_service.py).
from app.product.repositories.product_repository import ProductRepository

product_repository = ProductRepository()
stage_repository = StageRepository()


@bp.route("/", methods=["GET"])
def index():
    products = product_repository.all(order_by="id")
    stages = stage_repository.all(order_by="id")

    return render_template(
        "price/prices.html",
        title="Cadastro de Preço",
        products=products,
        stages=stages,
        missing_prices=ps.get_missing_prices(),
    )


# Partial de tabela de preços — mesmo padrão de
# production/table/partial e payment/history/partial.
@bp.route("/table/partial", methods=["GET"])
def table_partial():
    prices = ps.get_prices()

    return jsonify(
        render_template(
            "price/_table.html",
            prices=prices
        )
    )


# Definir ou atualizar o preço de uma combinação produto+etapa
@bp.route("/set", methods=["POST"])
def set_price():
    form = request.form
    raw_price = (form.get("price_per_dozen") or "").strip().replace(",", ".")
    try:
        price_per_dozen = Decimal(raw_price)
        product_id = int(form.get("product_id", ""))
        stage_id = int(form.get("stage_id", ""))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Produto, etapa ou preço inválido")

    dto = PriceSetDTO.from_form(
        product_id=product_id,
        stage_id=stage_id,
        price_per_dozen=price_per_dozen,
    )
    price = ps.set_price(dto)
    return jsonify(
        status="success",
        message="Preço salvo com sucesso",
        price_per_dozen=str(price.price_per_dozen),
    )


# Consultar o preço vigente de uma combinação — usado pelo formulário
# de produção para preencher price_per_dozen automaticamente ao
# selecionar produto+etapa. Retorna found=false (não 404) quando não
# há preço cadastrado, para o JS tratar como "sem preço definido,
# digite manualmente" em vez de erro.
@bp.route("/current", methods=["GET"])
def current_price():
    try:
        product_id = int(request.args["product_id"])
        stage_id = int(request.args["stage_id"])
    except (KeyError, ValueError):
        return jsonify(status="error", message="product_id e stage_id são obrigatórios")

    price = ps.get_current_price(product_id, stage_id)

    if price is None:
        return jsonify(status="success", found=False, price_per_dozen=None)

    return jsonify(status="success", found=True, price_per_dozen=str(price))
