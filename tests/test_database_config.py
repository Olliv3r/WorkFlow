from config import DEFAULT_DB_URL, normalize_database_url


def test_database_url_keeps_sqlite_default():
    assert normalize_database_url("") == DEFAULT_DB_URL
    assert normalize_database_url("sqlite:////tmp/workflow.db") == "sqlite:////tmp/workflow.db"


def test_database_url_normalizes_postgresql_to_psycopg():
    assert (
        normalize_database_url("postgresql://user:pass@localhost/workflow")
        == "postgresql+psycopg://user:pass@localhost/workflow"
    )
    assert (
        normalize_database_url("postgres://user:pass@localhost/workflow")
        == "postgresql+psycopg://user:pass@localhost/workflow"
    )
    explicit = "postgresql+psycopg://user:pass@localhost/workflow"
    assert normalize_database_url(explicit) == explicit


def test_database_url_normalizes_mysql_to_pymysql():
    assert (
        normalize_database_url("mysql://user:pass@localhost/workflow")
        == "mysql+pymysql://user:pass@localhost/workflow"
    )
    explicit = "mysql+pymysql://user:pass@localhost/workflow"
    assert normalize_database_url(explicit) == explicit
