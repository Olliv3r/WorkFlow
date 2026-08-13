from app.payment import bp
from flask import render_template, request, url_for, jsonify
from app.payment.services.payment_service import PaymentService as ps
from app.core.exceptions import NotFoundError, ValidationError, PermissionError

@bp.route("/", methods=["GET"])
def index():
    return render_template(
        "payment/payments.html",
        title="Pagamentos"
    )

# Renderizar cards
@bp.route("/cards/partial", methods=["GET"])
def cards_partial():
    productions = ps.get_productions()
    unpaid_count, total_dozens, total_amount = ps.get_unpaid_summary()
    start_period, end_period = ps.get_period()
  
    return jsonify(
        render_template(
            "payment/_cards_partial.html",
            productions=productions,
            total_dozens=total_dozens,
            total_amount=total_amount,
            start_period=start_period,
            end_period=end_period
        )
    )

# Renderizar historico
@bp.route("/history/partial", methods=["GET"])
def history_partial():
    payments = ps.get_payments()
    return jsonify(
        render_template(
            "payment/_history_table.html",
            payments=payments
        )
    )

# Criar pagamento
@bp.route("/create", methods=["POST"])
def create():
    ids = list(map(int, request.form.getlist("production_ids")))

    try:
        payment = ps.payment_create(ids)
        return jsonify(status="success", message="Pagamento criado com sucesso")

    except NotFoundError as error:
        return jsonify(status="error", message=str(error.message))

# Excluir pagamento
@bp.route("/<int:payment_id>/delete", methods=["POST"])
def delete(payment_id):
    try:
        is_delete = ps.payment_delete(payment_id)

        if not is_delete:
            return jsonify(status="error", message="Não foi possível excluir o pagamento")
  
        return jsonify(status="success", message="Pagamento excluido com sucesso")
      
    except (NotFoundError, PermissionError) as error:
        return jsonify(status="error", message=str(error.message))

# Atualizar o status do pagamento
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

