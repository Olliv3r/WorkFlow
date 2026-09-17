from flask import jsonify, request, render_template
from app.product import bp
from app.product.services.product_service import ProductService as ps
from app.product.dtos.product_create_dto import ProductCreateDTO
from app.core.exceptions import ValidationError


def _optional_int(form, key):
    raw = form.get(key)
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(f"Campo {key} inválido")


def _required_int(form, key):
    value = _optional_int(form, key)
    if value is None:
        raise ValidationError(f"Campo {key} é obrigatório")
    return value


@bp.route("/", methods=["GET"])
def index():
    options = ps.get_form_options()
    return render_template(
        "product/products.html",
        title="Produtos",
        products=ps.get_product_entities(),
        **options,
    )


@bp.route("/<int:product_id>/details", methods=["GET"])
def details(product_id):
    product = ps.get_product_entity(product_id)
    return render_template("product/details.html", title="Detalhes do produto", product=product)


@bp.route("/options", methods=["GET"])
def get_options():
    return jsonify(status="success", message="Dados de produtos encontrados", data=ps.get_products())


@bp.route("/create", methods=["POST"])
def create():
    form = request.form
    dto = ProductCreateDTO.from_form(
        family_id=_required_int(form, "family_id"),
        material_id=_required_int(form, "material_id"),
        hole_id=_optional_int(form, "hole_id"),
        stick_type_id=_required_int(form, "stick_type_id"),
        quality_id=_optional_int(form, "quality_id"),
    )
    product = ps.create(dto)
    return jsonify(status="success", message="Produto criado com sucesso", id=product.id)


@bp.route("/<int:product_id>/toggle-active", methods=["POST"])
def toggle_active(product_id):
    product = ps.toggle_active(product_id)
    return jsonify(status="success", message="Status do produto atualizado", active=product.active)
