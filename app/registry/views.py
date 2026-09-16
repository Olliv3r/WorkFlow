from flask import render_template, request, redirect, url_for
from sqlalchemy.exc import IntegrityError
from app.registry import bp
from app.extensions import db
from app.models import ProductFamily, Material, Quality, Hole, StickType, Stage
from app.core.exceptions import ValidationError, NotFoundError, ConflictError

CONFIG = {
 "families": (ProductFamily, "Famílias"), "materials": (Material, "Materiais"),
 "qualities": (Quality, "Qualidades"), "holes": (Hole, "Furos"),
 "stick-types": (StickType, "Tipos de taco"), "stages": (Stage, "Etapas")}

def get_cfg(kind):
    if kind not in CONFIG: raise NotFoundError("Cadastro não encontrado")
    return CONFIG[kind]

@bp.route("/")
def index(): return redirect(url_for("registry.manage", kind="families"))

@bp.route("/<kind>")
def manage(kind):
    model, label = get_cfg(kind)
    items = model.query.order_by(model.id).all()
    return render_template("registry/index.html", title="Cadastros", kind=kind, label=label, items=items, model=model)

@bp.route("/<kind>/save", methods=["POST"])
def save(kind):
    model, _ = get_cfg(kind); item_id=request.form.get("id"); item=db.session.get(model, int(item_id)) if item_id else model()
    if item_id and not item: raise NotFoundError("Registro não encontrado")
    if model is Hole:
        try: q=int(request.form.get("quantity", ""))
        except ValueError: raise ValidationError("Quantidade de furos inválida")
        if q <= 0: raise ValidationError("Quantidade de furos deve ser positiva")
        duplicate=Hole.query.filter(Hole.quantity==q, Hole.id != (item.id or 0)).first()
        if duplicate: raise ConflictError(f"Já existe um cadastro para {q} furos")
        item.quantity=q
    else:
        name=(request.form.get("name") or "").strip()
        if not name: raise ValidationError("Nome é obrigatório")
        item.name=name
    if hasattr(item,"description"): item.description=(request.form.get("description") or "").strip() or None
    if isinstance(item, Stage):
        try: item.order=int(request.form.get("order") or 1)
        except ValueError: raise ValidationError("Ordem inválida")
    if not item_id: db.session.add(item)
    try: db.session.commit()
    except IntegrityError:
        db.session.rollback(); raise ConflictError("Já existe um cadastro com esses dados")
    return redirect(url_for("registry.manage", kind=kind))

@bp.route("/<kind>/<int:item_id>/delete", methods=["POST"])
def delete(kind,item_id):
    model,_=get_cfg(kind); item=db.session.get(model,item_id)
    if not item: raise NotFoundError("Registro não encontrado")
    if hasattr(item,"active"):
        item.active=False; db.session.commit(); return redirect(url_for("registry.manage",kind=kind))
    if getattr(item,"products", None) or getattr(item,"productions", None):
        raise ConflictError("Não é possível excluir: este cadastro está sendo utilizado")
    try: db.session.delete(item); db.session.commit()
    except IntegrityError:
        db.session.rollback(); raise ConflictError("Não é possível excluir: este cadastro está sendo utilizado")
    return redirect(url_for("registry.manage",kind=kind))
