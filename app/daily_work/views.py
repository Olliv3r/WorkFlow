from datetime import date
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, url_for
from app.daily_work import bp
from app.extensions import db
from app.models import DailyWork
from app.core.exceptions import ValidationError, NotFoundError, PermissionError

@bp.route("/")
def index():
    items = DailyWork.query.order_by(DailyWork.date.desc(), DailyWork.id.desc()).all()
    return render_template("daily_work/index.html", title="Diárias", items=items)

@bp.route("/create", methods=["POST"])
def create():
    period = (request.form.get("period") or "").strip()
    try:
        amount = Decimal(request.form.get("amount", "").replace(",", "."))
        work_date = date.fromisoformat(request.form.get("date", ""))
    except (InvalidOperation, ValueError):
        raise ValidationError("Dados da diária inválidos")
    if period not in ("Inteira", "Meia", "Outro parcial") or amount <= 0:
        raise ValidationError("Informe o período e um valor positivo para a diária")
    fraction = Decimal("1.0") if period == "Inteira" else Decimal("0.5") if period == "Meia" else None
    item = DailyWork(date=work_date, fraction=fraction, period=period,
        daily_rate=amount, total_amount=amount,
        description=(request.form.get("description") or "Serviços variados de auxílio").strip(),
        observation=(request.form.get("observation") or "").strip() or None)
    db.session.add(item); db.session.commit()
    return redirect(url_for("daily_work.index"))


@bp.route("/<int:item_id>")
def details(item_id):
    item = db.session.get(DailyWork, item_id)
    if not item: raise NotFoundError("Diária não encontrada")
    return render_template("daily_work/details.html", title=f"Diária #{item.id}", item=item)

@bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
def edit(item_id):
    item = db.session.get(DailyWork, item_id)
    if not item: raise NotFoundError("Diária não encontrada")
    if item.payment_id: raise PermissionError("Não é possível editar uma diária vinculada a pagamento")
    if request.method == "POST":
        period = (request.form.get("period") or "").strip()
        try:
            amount = Decimal(request.form.get("amount", "").replace(",", "."))
            work_date = date.fromisoformat(request.form.get("date", ""))
        except (InvalidOperation, ValueError):
            raise ValidationError("Dados da diária inválidos")
        if period not in ("Inteira", "Meia", "Outro parcial") or amount <= 0:
            raise ValidationError("Informe o período e um valor positivo para a diária")
        item.date = work_date
        item.period = period
        item.fraction = Decimal("1.0") if period == "Inteira" else Decimal("0.5") if period == "Meia" else None
        item.daily_rate = amount
        item.total_amount = amount
        item.description = (request.form.get("description") or "Serviços variados de auxílio").strip()
        item.observation = (request.form.get("observation") or "").strip() or None
        db.session.commit()
        return redirect(url_for("daily_work.details", item_id=item.id))
    return render_template("daily_work/edit.html", title=f"Editar diária #{item.id}", item=item)

@bp.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    item = db.session.get(DailyWork, item_id)
    if not item: raise NotFoundError("Diária não encontrada")
    if item.payment_id: raise PermissionError("Não é possível excluir uma diária vinculada a pagamento")
    db.session.delete(item); db.session.commit()
    return redirect(url_for("daily_work.index"))
