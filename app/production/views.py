from datetime import date
from decimal import Decimal, InvalidOperation
from flask import render_template, request, jsonify

from app.production import bp
from app.production.services.production_service import ProductionService as ps
from app.production.dtos.production_dto import ProductionCreateDTO
from app.core.exceptions import ValidationError


def _parse_filters(args):
    def parse_date(name):
        raw = args.get(name)
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None

    product_id = None
    raw_product = args.get("product_id")
    if raw_product:
        try:
            product_id = int(raw_product)
        except ValueError:
            pass
    return parse_date("start_date"), parse_date("end_date"), product_id


def _int_field(form, key):
    try:
        value = int(form.get(key, ""))
    except (TypeError, ValueError):
        raise ValidationError(f"Campo {key} inválido")
    return value


def _decimal_field(form, key):
    raw = (form.get(key) or "").strip().replace(",", ".")
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError):
        raise ValidationError("Preço por dúzia inválido")
    if value <= 0:
        raise ValidationError("Preço por dúzia deve ser maior que zero")
    return value


def _date_field(form, key, required=True):
    raw = (form.get(key) or "").strip()
    if not raw and not required:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ValidationError("Data inválida")


def _build_dto(form, include_date=True):
    dozens = _int_field(form, "dozens")
    if dozens <= 0:
        raise ValidationError("Quantidade de dúzias deve ser maior que zero")
    return ProductionCreateDTO.from_form(
        product_id=_int_field(form, "product_id"),
        stage_id=_int_field(form, "stage_id"),
        dozens=dozens,
        price_per_dozen=_decimal_field(form, "price_per_dozen"),
        date=_date_field(form, "date") if include_date else None,
        observation=(form.get("observation") or "").strip() or None,
    )


@bp.route("/", methods=["GET"])
def index():
    products = ps.get_products()
    stages = ps.get_stages()
    return render_template("production/productions.html", title="Gerenciar produções", products=products, stages=stages)


@bp.route("/cards/partial", methods=["GET"])
def cards_partial():
    start_date, end_date, product_id = _parse_filters(request.args)
    productions = ps.get_productions(start_date, end_date, product_id)
    total_summary = ps.get_total_summary(start_date, end_date, product_id)
    unpaid_summary = ps.get_unpaid_summary(start_date, end_date, product_id)
    return jsonify(render_template(
        "production/_cards.html",
        productions=productions,
        total_dozens=total_summary.total_dozens,
        total_amount=total_summary.total_amount,
        unpaid_count=unpaid_summary.production_count,
        unpaid_amount=unpaid_summary.total_amount,
    ))


@bp.route("/table/partial", methods=["GET"])
def table_partial():
    start_date, end_date, product_id = _parse_filters(request.args)
    return jsonify(render_template("production/_table.html", productions=ps.get_productions(start_date, end_date, product_id)))


@bp.route("/create", methods=["POST"])
def create():
    ps.production_create(_build_dto(request.form, include_date=True))
    return jsonify(status="success", message="Produção registrada com sucesso")


@bp.route("/<int:production_id>/details", methods=["GET"])
def details(production_id):
    production = ps.get_production(production_id)
    return render_template(
        "production/details.html",
        title=f"Produção #{production.id}",
        production=production,
    )


@bp.route("/<int:production_id>/data", methods=["GET"])
def get_data(production_id):
    return jsonify(status="success", message="Dados de produção encontrados", data=ps.get_data(production_id))


@bp.route("/<int:production_id>/edit", methods=["POST"])
def edit_data(production_id):
    ps.edit(production_id, _build_dto(request.form, include_date=True))
    return jsonify(status="success", message="Dados editados com sucesso")


@bp.route("/<int:production_id>/delete", methods=["POST"])
def delete(production_id):
    ps.production_delete(production_id)
    return jsonify(status="success", message="Produção excluída com sucesso")
