from datetime import date
from pathlib import Path

from flask import render_template, send_file

from app.main import bp
from app.extensions import db
from app.report.services.report_service import ReportService


@bp.route("/", methods=["GET"])
def index():
    dashboard = ReportService.dashboard_data()
    return render_template(
        "main/index.html",
        title="Dashboard",
        **dashboard,
    )


@bp.route("/backup/download", methods=["GET"])
def download_backup():
    from app.core.exceptions import NotFoundError, ValidationError

    engine_url = db.engine.url
    if engine_url.get_backend_name() != "sqlite":
        raise ValidationError(
            "Backup direto pelo WorkFlow está disponível apenas para SQLite. "
            "Em PostgreSQL/MySQL, utilize o backup do servidor/provedor do banco."
        )

    database = engine_url.database
    if not database:
        raise NotFoundError("Arquivo do banco de dados não encontrado")

    db_path = Path(database)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    if not db_path.exists():
        raise NotFoundError("Arquivo do banco de dados não encontrado")

    return send_file(
        db_path,
        as_attachment=True,
        download_name=f"workflow-backup-{date.today().isoformat()}.db",
    )
