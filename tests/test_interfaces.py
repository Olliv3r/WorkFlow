from pathlib import Path


def test_payment_page_has_only_footer_create_button():
    page = Path("app/templates/payment/payments.html").read_text(encoding="utf-8")
    partial = Path("app/templates/payment/_cards_partial.html").read_text(encoding="utf-8")

    assert "Novo Pagamento" not in page
    assert "Novo pagamento" not in page
    assert partial.count('id="btnCreate"') == 1
    assert "Criar Pagamento" in partial


def test_remaining_payment_button_is_bound_to_create_flow():
    partial = Path("app/templates/payment/_cards_partial.html").read_text(encoding="utf-8")
    events = Path("app/static/js/modules/payment/payment.events.js").read_text(encoding="utf-8")
    api = Path("app/static/js/modules/payment/payment.api.js").read_text(encoding="utf-8")

    assert 'id="formPaymentCreate"' in partial
    assert 'id="btnCreate" type="submit"' in partial
    assert '"#formPaymentCreate"' in events
    assert 'url: "/payment/create"' in api


def test_main_screens_render_after_seed(seeded):
    client = seeded.test_client()
    for path in ["/", "/production/", "/payment/", "/product/", "/price/", "/report/"]:
        response = client.get(path)
        assert response.status_code == 200, path


def test_analytics_assets_are_present_on_dashboard_and_reports():
    dashboard = Path("app/templates/main/index.html").read_text(encoding="utf-8")
    reports = Path("app/templates/report/reports.html").read_text(encoding="utf-8")
    analytics_js = Path("app/static/js/modules/report/analytics.js")
    analytics_css = Path("app/static/css/analytics.css")

    assert 'id="dashboardTrendData"' in dashboard
    assert 'id="reportTrendData"' in reports
    assert 'id="productChartData"' in reports
    assert 'id="stageChartData"' in reports
    assert analytics_js.exists()
    assert analytics_css.exists()


def test_sidebar_only_exposes_direct_backup_for_sqlite():
    sidebar = Path("app/templates/sidebar.html").read_text(encoding="utf-8")
    assert "database_backend_name" in sidebar
    assert "direct_database_backup" in sidebar
    assert "main.download_backup" in sidebar


def test_dashboard_uses_production_summary_column_names():
    dashboard = Path("app/templates/main/index.html").read_text(encoding="utf-8")

    assert "today_summary.total_dozens" in dashboard
    assert "today_summary.total_amount" in dashboard
    assert "week_summary.total_dozens" in dashboard
    assert "week_summary.production_count" in dashboard
    assert "month_summary.total_dozens" in dashboard
    assert "month_summary.total_amount" in dashboard

    assert "today_summary.dozens" not in dashboard
    assert "today_summary.amount" not in dashboard
    assert "week_summary.dozens" not in dashboard
    assert "week_summary.count" not in dashboard
    assert "month_summary.dozens" not in dashboard
    assert "month_summary.amount" not in dashboard


def test_receivables_page_supports_multi_payment_allocation():
    page = Path("app/templates/payment/receivables.html").read_text(encoding="utf-8")

    assert 'name="allocation_payment_ids"' in page
    assert 'id="selectAllPending"' in page
    assert 'id="clearPending"' in page
    assert 'Valor deste recebimento' in page
    assert 'Sem seleção' in page
