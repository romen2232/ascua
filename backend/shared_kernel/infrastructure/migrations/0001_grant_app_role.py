"""Grant the runtime role access to every table the owner creates from now on.

Every other app's first migration depends on this one, so no table is created before the
default privileges are in place.
"""

from django.db import migrations

GRANT = """
GRANT USAGE ON SCHEMA public TO ascua_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ascua_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO ascua_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ascua_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ascua_app;
"""

REVOKE = """
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM ascua_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE USAGE, SELECT ON SEQUENCES FROM ascua_app;
"""


class Migration(migrations.Migration):
    initial = True
    dependencies: list[tuple[str, str]] = []
    operations = [migrations.RunSQL(GRANT, REVOKE)]
