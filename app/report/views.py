import csv
from datetime import date
from io import StringIO

from flask import render_template, request, Response

from app.report import bp
from app.report.services.report_service import ReportService as rs
from app.extensions import db
from app.models import Production


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


@bp.route("/export.csv", methods=["GET"])
def export_csv():
    start_date, end_date = _period(request.args)
    query = db.session.query(Production)
    if start_date:
        query = query.filter(Production.date >= start_date)
    if end_date:
        query = query.filter(Production.date <= end_date)
    productions = query.order_by(Production.date.asc(), Production.id.asc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["data", "produto", "material", "furos", "etapa", "duzias", "preco_por_duzia", "total", "pagamento"])
    for p in productions:
        writer.writerow([
            p.date.isoformat(),
            p.product.family.name,
            p.product.material.name,
            p.product.hole.quantity,
            p.stage.name,
            p.dozens,
            f"{p.price_per_dozen:.2f}",
            f"{p.total_amount:.2f}",
            p.payment.status if p.payment else "sem_pagamento",
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=producoes.csv"},
    )
