from app.payment import bp
from flask import render_template, request, url_for, jsonify
from app.payment.services.payment_service import PaymentService as ps
from app.core.exceptions import NotFoundError, ValidationError


@bp.route(
    "/",
    methods=[
        "GET",
    ],
)
def index():
    productions = ps.get_productions()
    payments = ps.get_payments()
    total_dozens, total_amount = ps.get_unpaid_summary()
    start_period, end_period = ps.get_period()

    return render_template(
        "payment/payments.html",
        title="Pagamentos",
        productions=productions,
        payments=payments,
        start_period=start_period,
        end_period=end_period,
        total_dozens=total_dozens,
        total_amount=total_amount,
    )


@bp.route("/create", methods=["GET", "POST"])
def create():
    ids = list(map(int, request.form.getlist("production_ids")))

    payment = ps.payment_create(ids)
    return jsonify(status="success", message="Pagamento criado com sucesso")


@bp.route("/<int:payment_id>/toggle-status", methods=["POST"])
def toggle_status(payment_id):
    try:
        payment = ps.toggle_status(payment_id)
        payment_date = (
            payment.payment_date.isoformat() if payment.payment_date else None
        )

        return jsonify(
            status="success",
            message="Status de pagamento atualizado",
            id=payment.id,
            payment_status=payment.status,
            payment_date=payment_date,
        )

    except (NotFoundError, ValidationError) as error:
        return jsonify(
            status="error", message="Erro ao atualizar o status de pagamento"
        )
