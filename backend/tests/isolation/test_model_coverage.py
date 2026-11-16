from django.apps import apps
from django.db import connection

from shared_kernel.infrastructure.tenancy import TenantManager
from tests.isolation.registry import EXEMPT_APP_LABELS, TENANT_MODELS_EXEMPT


def _forced_rls(table: str) -> bool:
    with connection.cursor() as c:
        c.execute(
            "SELECT relrowsecurity AND relforcerowsecurity FROM pg_class WHERE relname = %s",
            [table],
        )
        row = c.fetchone()
    return bool(row and row[0])


def test_every_model_is_tenant_scoped_or_exempt(db):
    problems = []
    for model in apps.get_models():
        meta = model._meta
        if meta.app_label in EXEMPT_APP_LABELS or meta.label in TENANT_MODELS_EXEMPT:
            continue
        if not meta.managed or meta.proxy:
            continue
        if not isinstance(model._default_manager, TenantManager):
            problems.append(f"{meta.label}: default manager is not a TenantManager")
        if not _forced_rls(meta.db_table):
            problems.append(f"{meta.label}: table {meta.db_table} lacks forced RLS")
    assert not problems, "\n".join(problems)


def test_exemptions_point_at_real_models():
    labels = {m._meta.label for m in apps.get_models()}
    assert set(TENANT_MODELS_EXEMPT) <= labels
