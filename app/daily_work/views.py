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
    try:
        fraction = Decimal(request.form.get("fraction", ""))
        rate = Decimal(request.form.get("daily_rate", "").replace(",", "."))
        work_date = date.fromisoformat(request.form.get("date", ""))
    except (InvalidOperation, ValueError):
        raise ValidationError("Dados da diária inválidos")
    if fraction not in (Decimal("0.5"), Decimal("1.0")) or rate <= 0:
        raise ValidationError("A diária deve ser inteira ou meia e possuir valor positivo")
    item = DailyWork(date=work_date, fraction=fraction, daily_rate=rate,
        total_amount=(rate * fraction).quantize(Decimal("0.01")),
        description=(request.form.get("description") or "Acabamentos e serviços auxiliares").strip(),
        observation=(request.form.get("observation") or "").strip() or None)
    db.session.add(item); db.session.commit()
    return redirect(url_for("daily_work.index"))

@bp.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    item = db.session.get(DailyWork, item_id)
    if not item: raise NotFoundError("Diária não encontrada")
    if item.payment_id: raise PermissionError("Não é possível excluir uma diária vinculada a pagamento")
    db.session.delete(item); db.session.commit()
    return redirect(url_for("daily_work.index"))
