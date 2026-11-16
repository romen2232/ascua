from django.db import connection


def test_database_is_postgres_17(db):
    with connection.cursor() as c:
        c.execute("SHOW server_version_num")
        assert int(c.fetchone()[0]) // 10000 == 17


def test_runtime_role_cannot_bypass_rls(db):
    with connection.cursor() as c:
        c.execute("SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user")
        assert c.fetchone()[0] is False


def test_tests_run_as_runtime_role(db):
    with connection.cursor() as c:
        c.execute("SELECT current_user")
        assert c.fetchone()[0] == "ascua_app"
