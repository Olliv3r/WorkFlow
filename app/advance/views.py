from datetime import date
from decimal import Decimal, InvalidOperation
from flask import render_template, request, redirect, url_for
from app.advance import bp
from app.extensions import db
from app.models import Advance, Payment, AdvanceDeduction
from app.core.exceptions import ValidationError, NotFoundError, PermissionError


def _pending_payments():
    return [p for p in Payment.query.order_by(Payment.start_period.desc(), Payment.id.desc()).all()
            if p.pending_amount > 0]


def _apply_to_payment(advance, payment):
    """Compensa somente o fechamento explicitamente escolhido/resolvido.

    Nunca espalha o restante do vale por outras pendências. Se o fechamento
    escolhido não for suficiente, o saldo do vale continua pendente para
    fechamentos futuros.
    """
    amount = min(advance.balance, payment.pending_amount)
    if amount > 0:
        db.session.add(AdvanceDeduction(
            advance=advance, payment=payment, amount=amount, kind="receivable"
        ))
        db.session.flush()
    return amount


@bp.route("/")
def index():
    items = Advance.query.order_by(Advance.date.desc(), Advance.id.desc()).all()
    pending = sum((a.balance for a in items if a.balance > 0), Decimal("0.00"))
    payments = _pending_payments()
    return render_template("advance/index.html", title="Vales", items=items,
                           pending=pending, payments=payments)


@bp.route("/create", methods=["POST"])
def create():
    try:
        amount = Decimal(request.form.get("amount", "").replace(",", "."))
        advance_date = date.fromisoformat(request.form.get("date", ""))
    except (InvalidOperation, ValueError):
        raise ValidationError("Dados do vale inválidos")
    if amount <= 0:
        raise ValidationError("O valor do vale deve ser positivo")

    mode = (request.form.get("allocation_mode") or "automatic").strip()
    if mode not in ("automatic", "manual", "future"):
        raise ValidationError("Modo de abatimento inválido")

    if request.form.get("allocation_confirmed") != "yes":
        raise ValidationError("Confirme o destino do vale antes de registrá-lo")

    pending_payments = _pending_payments()
    target = None
    if pending_payments:
        if mode == "automatic":
            # Regra confirmada: automático usa somente a pendência mais recente.
            target = pending_payments[0]
        elif mode == "manual":
            raw_id = request.form.get("payment_id")
            if not raw_id:
                raise ValidationError("Escolha o pagamento pendente que receberá o abatimento")
            try:
                payment_id = int(raw_id)
            except ValueError:
                raise ValidationError("Pagamento selecionado inválido")
            target = next((p for p in pending_payments if p.id == payment_id), None)
            if target is None:
                raise ValidationError("O pagamento escolhido não possui saldo pendente")
        else:
            # Próximo fechamento: não toca em nenhuma pendência atual.
            # Sem deduções, o vale permanece pendente e o PaymentService o
            # consumirá via FIFO somente ao criar fechamentos futuros.
            target = None

    item = Advance(date=advance_date, amount=amount,
                   observation=(request.form.get("observation") or "").strip() or None)
    try:
        db.session.add(item)
        db.session.flush()
        if target is not None:
            _apply_to_payment(item, target)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return redirect(url_for("advance.details", item_id=item.id))


@bp.route("/<int:item_id>")
def details(item_id):
    item = db.session.get(Advance, item_id)
    if not item:
        raise NotFoundError("Vale não encontrado")
    return render_template("advance/details.html", title=f"Vale #{item.id}", item=item)


@bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
def edit(item_id):
    item = db.session.get(Advance, item_id)
    if not item:
        raise NotFoundError("Vale não encontrado")
    if item.deductions:
        raise PermissionError("Este vale já possui abatimento e não pode ser alterado. Vales abatidos não têm desfazer.")
    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount", "").replace(",", "."))
            advance_date = date.fromisoformat(request.form.get("date", ""))
        except (InvalidOperation, ValueError):
            raise ValidationError("Dados do vale inválidos")
        if amount <= 0:
            raise ValidationError("O valor do vale deve ser positivo")
        item.date = advance_date
        item.amount = amount
        item.observation = (request.form.get("observation") or "").strip() or None
        db.session.commit()
        return redirect(url_for("advance.details", item_id=item.id))
    return render_template("advance/edit.html", title=f"Editar vale #{item.id}", item=item)


@bp.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    item = db.session.get(Advance, item_id)
    if not item:
        raise NotFoundError("Vale não encontrado")
    if item.deductions:
        raise PermissionError("Não é possível excluir um vale que já possui abatimentos. Vales abatidos não têm desfazer.")
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("advance.index"))
