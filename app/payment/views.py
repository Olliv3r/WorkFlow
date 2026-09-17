from datetime import date, timedelta
from flask import render_template, request, jsonify
from app.payment import bp
from app.payment.services.payment_service import PaymentService as ps
from app.core.exceptions import AppException, ValidationError


def _parse_period_filters(args):
    def parse(name):
        raw = args.get(name)
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return parse("start_date"), parse("end_date")


def _quick_period(name):
    today = date.today()
    if name == "today":
        return today, today
    if name == "this_week":
        return today - timedelta(days=today.weekday()), today
    if name == "last_week":
        this_start = today - timedelta(days=today.weekday())
        return this_start - timedelta(days=7), this_start - timedelta(days=1)
    if name == "last_15":
        return today - timedelta(days=14), today
    if name == "this_month":
        return today.replace(day=1), today
    return None, None


@bp.route("/", methods=["GET"])
def index():
    return render_template("payment/payments.html", title="Pagamentos")


@bp.route("/cards/partial", methods=["GET"])
def cards_partial():
    start_date, end_date = _parse_period_filters(request.args)
    quick = request.args.get("quick")
    if quick:
        start_date, end_date = _quick_period(quick)

    productions = ps.get_productions(start_date, end_date)
    daily_works = ps.get_daily_works(start_date, end_date)
    summary = ps.get_unpaid_summary(start_date, end_date)
    start_period, end_period = ps.get_period(start_date, end_date)
    daily_total = sum((d.total_amount for d in daily_works), 0)

    return jsonify(render_template(
        "payment/_cards_partial.html",
        productions=productions,
        daily_works=daily_works,
        total_dozens=summary.total_dozens,
        total_amount=summary.total_amount + daily_total,
        start_period=start_period,
        end_period=end_period,
    ))


@bp.route("/history/partial", methods=["GET"])
def history_partial():
    return jsonify(render_template("payment/_history_table.html", payments=ps.get_payments()))


@bp.route("/<int:payment_id>/details", methods=["GET"])
def details(payment_id):
    payment = ps.get_payment(payment_id)
    return render_template("payment/details.html", title=f"Pagamento #{payment.id}", payment=payment)


@bp.route("/create", methods=["POST"])
def create():
    raw_ids = request.form.getlist("production_ids")
    try:
        ids = [int(value) for value in raw_ids]
    except (TypeError, ValueError):
        raise ValidationError("IDs de produção inválidos")
    try:
        daily_ids = [int(value) for value in request.form.getlist("daily_work_ids")]
    except (TypeError, ValueError):
        raise ValidationError("IDs de diária inválidos")
    payment = ps.payment_create(ids, request.form.get("observation"), daily_ids)
    return jsonify(status="success", message="Fechamento criado com sucesso")


@bp.route("/<int:payment_id>/delete", methods=["POST"])
def delete(payment_id):
    ps.payment_delete(payment_id)
    return jsonify(status="success", message="Pagamento excluído com sucesso")


@bp.route("/<int:payment_id>/toggle-status", methods=["POST"])
def toggle_status(payment_id):
    payment = ps.toggle_status(payment_id)
    return jsonify(
        status="success",
        message="Status de pagamento atualizado",
        id=payment.id,
        payment_status=payment.status,
        payment_date=payment.payment_date.isoformat() if payment.payment_date else None,
    )


@bp.route("/receipt/create", methods=["POST"])
def receipt_create():
    payment_id = request.form.get("payment_id") or None
    receipt = ps.register_receipt(
        request.form.get("amount"),
        request.form.get("date"),
        request.form.get("observation"),
        payment_id,
    )
    return jsonify(status="success", message="Recebimento registrado com sucesso", id=receipt.id)


@bp.route("/receivables", methods=["GET"])
def receivables():
    payments = ps.get_payments()
    return render_template(
        "payment/receivables.html", title="Pendências e recebimentos",
        payments=payments, receipts=ps.get_receipts(), summary=ps.get_receivables_summary()
    )
