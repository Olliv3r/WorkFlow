from datetime import date
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, url_for
from app.advance import bp
from app.extensions import db
from app.models import Advance
from app.core.exceptions import ValidationError, NotFoundError, PermissionError

@bp.route("/")
def index():
    items = Advance.query.order_by(Advance.date.desc(), Advance.id.desc()).all()
    pending = sum((a.balance for a in items if a.balance > 0), Decimal("0.00"))
    return render_template("advance/index.html", title="Vales", items=items, pending=pending)

@bp.route("/create", methods=["POST"])
def create():
    try:
        amount = Decimal(request.form.get("amount", "").replace(",", "."))
        advance_date = date.fromisoformat(request.form.get("date", ""))
    except (InvalidOperation, ValueError): raise ValidationError("Dados do vale inválidos")
    if amount <= 0: raise ValidationError("O valor do vale deve ser positivo")
    item = Advance(date=advance_date, amount=amount, observation=(request.form.get("observation") or "").strip() or None)
    db.session.add(item); db.session.commit()
    return redirect(url_for("advance.index"))

@bp.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    item = db.session.get(Advance, item_id)
    if not item: raise NotFoundError("Vale não encontrado")
    if item.deductions: raise PermissionError("Não é possível excluir um vale que já possui abatimentos")
    db.session.delete(item); db.session.commit()
    return redirect(url_for("advance.index"))
