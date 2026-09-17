import csv
from datetime import date
from io import StringIO, BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from flask import render_template, request, Response

from app.report import bp
from app.report.services.report_service import ReportService as rs
from app.extensions import db
from app.models import (Production, DailyWork, Payment, Advance, AdvanceDeduction, Receipt, ReceiptAllocation)


def _period(args):
    def parse(name):
        raw = args.get(name)
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return parse("start_date"), parse("end_date")


@bp.route("/", methods=["GET"])
def index():
    start_date, end_date = _period(request.args)
    pending_summary = rs.get_pending_summary()
    pending_payments = rs.get_pending_payments()
    summary = rs.production_summary(start_date, end_date)

    return render_template(
        "report/reports.html",
        title="Relatórios",
        payment_count=pending_summary.payment_count,
        pending_total_dozens=pending_summary.total_dozens,
        pending_total_amount=pending_summary.total_amount,
        pending_payments=pending_payments,
        summary=summary,
        by_product=rs.by_product(start_date, end_date),
        by_stage=rs.by_stage(start_date, end_date),
        by_day=rs.by_day(start_date, end_date),
        trend=rs.trend(start_date, end_date),
        comparison=rs.comparison(start_date, end_date),
        product_chart=rs.product_chart(start_date, end_date),
        stage_chart=rs.stage_chart(start_date, end_date),
        start_date=start_date,
        end_date=end_date,
    )


def _in_period(query, column, start_date, end_date):
    if start_date:
        query = query.filter(column >= start_date)
    if end_date:
        query = query.filter(column <= end_date)
    return query


def _csv_text(headers, rows):
    """CSV amigável a Excel/Calc, mantendo valores numéricos sem símbolo monetário."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return "\ufeff" + output.getvalue()


@bp.route("/export.csv", methods=["GET"])
def export_csv():
    """Compatibilidade: exporta apenas as produções, agora com o fechamento identificado."""
    start_date, end_date = _period(request.args)
    query = _in_period(db.session.query(Production), Production.date, start_date, end_date)
    productions = query.order_by(Production.date.asc(), Production.id.asc()).all()

    rows = []
    for p in productions:
        payment = p.payment
        rows.append([
            p.id,
            p.date.isoformat(),
            p.product.family.name,
            p.product.material.name,
            p.product.hole.quantity if p.product.hole else "",
            p.stage.name,
            p.dozens,
            f"{p.price_per_dozen:.2f}",
            f"{p.total_amount:.2f}",
            payment.id if payment else "",
            payment.receipt_status if payment else "sem_fechamento",
        ])

    content = _csv_text(
        ["producao_id", "data", "produto", "material", "furos", "etapa", "duzias",
         "preco_por_duzia", "total", "fechamento_id", "situacao_recebimento"],
        rows,
    )
    return Response(content, mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=producoes.csv"})


@bp.route("/export.zip", methods=["GET"])
def export_financial_zip():
    """Exportação completa: trabalho, fechamentos, vales e dinheiro efetivamente recebido.

    Cada conceito fica em seu próprio CSV para não duplicar totais financeiros nas linhas
    de produção. O período, quando informado, é aplicado à data natural de cada registro.
    """
    start_date, end_date = _period(request.args)

    productions = _in_period(Production.query, Production.date, start_date, end_date).order_by(Production.date, Production.id).all()
    daily_works = _in_period(DailyWork.query, DailyWork.date, start_date, end_date).order_by(DailyWork.date, DailyWork.id).all()
    payments = _in_period(Payment.query, Payment.end_period, start_date, end_date).order_by(Payment.end_period, Payment.id).all()
    advances = _in_period(Advance.query, Advance.date, start_date, end_date).order_by(Advance.date, Advance.id).all()
    receipts = _in_period(Receipt.query, Receipt.date, start_date, end_date).order_by(Receipt.date, Receipt.id).all()

    payment_ids = [p.id for p in payments]
    advance_ids = [a.id for a in advances]
    receipt_ids = [r.id for r in receipts]
    # Um abatimento pode ser relevante porque o vale está no período OU porque
    # o fechamento afetado está no período. Isso é especialmente importante
    # para vales posteriores compensados contra uma pendência existente.
    deduction_query = AdvanceDeduction.query
    if start_date or end_date:
        from sqlalchemy import or_
        conditions = []
        if payment_ids:
            conditions.append(AdvanceDeduction.payment_id.in_(payment_ids))
        if advance_ids:
            conditions.append(AdvanceDeduction.advance_id.in_(advance_ids))
        deductions = (deduction_query.filter(or_(*conditions)).order_by(
            AdvanceDeduction.payment_id, AdvanceDeduction.id
        ).all() if conditions else [])
    else:
        deductions = deduction_query.order_by(AdvanceDeduction.payment_id, AdvanceDeduction.id).all()
    allocations = (ReceiptAllocation.query.filter(ReceiptAllocation.receipt_id.in_(receipt_ids)).order_by(ReceiptAllocation.receipt_id, ReceiptAllocation.id).all() if receipt_ids else [])

    files = {
        "producoes.csv": _csv_text(
            ["producao_id", "data", "produto", "material", "furos", "etapa", "duzias", "preco_por_duzia", "total", "fechamento_id"],
            [[p.id, p.date.isoformat(), p.product.family.name, p.product.material.name,
              p.product.hole.quantity if p.product.hole else "", p.stage.name, p.dozens,
              f"{p.price_per_dozen:.2f}", f"{p.total_amount:.2f}", p.payment_id or ""] for p in productions]
        ),
        "diarias.csv": _csv_text(
            ["diaria_id", "data", "periodo", "valor", "descricao", "observacao", "fechamento_id"],
            [[d.id, d.date.isoformat(), d.period, f"{d.total_amount:.2f}",
              d.description, d.observation or "", d.payment_id or ""] for d in daily_works]
        ),
        "fechamentos.csv": _csv_text(
            ["fechamento_id", "inicio_periodo", "fim_periodo", "bruto", "vales_abatidos", "liquido_devido",
             "recebido_vinculado", "pendente_identificado", "situacao_recebimento", "duzias", "observacao"],
            [[p.id, p.start_period.isoformat(), p.end_period.isoformat(), f"{p.gross_amount:.2f}",
              f"{p.advance_amount:.2f}", f"{p.net_amount:.2f}", f"{p.received_amount:.2f}",
              f"{p.pending_amount:.2f}", p.receipt_status, p.total_dozens, p.observation or ""] for p in payments]
        ),
        "vales.csv": _csv_text(
            ["vale_id", "data", "original", "abatido", "saldo", "situacao", "destino_saldo_restante", "observacao"],
            [[a.id, a.date.isoformat(), f"{a.amount:.2f}", f"{a.deducted_amount:.2f}",
              f"{a.balance:.2f}", a.status,
              "proximo_fechamento" if a.balance > 0 else "quitado", a.observation or ""] for a in advances]
        ),
        "abatimentos_vales.csv": _csv_text(
            ["abatimento_id", "vale_id", "fechamento_id", "origem_abatimento", "valor_abatido"],
            [[d.id, d.advance_id, d.payment_id,
              "no_fechamento" if d.kind == "closing" else "compensacao_de_pendencia",
              f"{d.amount:.2f}"] for d in deductions]
        ),
        "recebimentos.csv": _csv_text(
            ["recebimento_id", "data", "valor_recebido", "valor_vinculado", "valor_nao_identificado", "observacao"],
            [[r.id, r.date.isoformat(), f"{r.amount:.2f}", f"{r.allocated_amount:.2f}",
              f"{r.unallocated_amount:.2f}", r.observation or ""] for r in receipts]
        ),
        "alocacoes_recebimentos.csv": _csv_text(
            ["alocacao_id", "recebimento_id", "fechamento_id", "valor"],
            [[a.id, a.receipt_id, a.payment_id, f"{a.amount:.2f}"] for a in allocations]
        ),
    }

    memory = BytesIO()
    with ZipFile(memory, "w", ZIP_DEFLATED) as archive:
        for filename, content in files.items():
            archive.writestr(filename, content.encode("utf-8"))
    memory.seek(0)
    return Response(memory.getvalue(), mimetype="application/zip",
                    headers={"Content-Disposition": "attachment; filename=workflow-exportacao.zip"})
