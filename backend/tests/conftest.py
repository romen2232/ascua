"""Run every test as the runtime role so row-level security applies exactly as in production.

The test database is created and migrated as ascua_owner; after that every connection to it
switches to ascua_app.
"""

from collections.abc import Iterator
from typing import Any

import pytest
from django.db import connection
from django.db.backends.signals import connection_created


def _drop_to_app_role(sender: Any, connection: Any, **_: Any) -> None:
    if connection.settings_dict["NAME"].startswith("test_"):
        with connection.cursor() as cursor:
            cursor.execute("SET ROLE ascua_app")


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup: None, django_db_blocker: Any) -> Iterator[None]:
    with django_db_blocker.unblock():
        connection_created.connect(_drop_to_app_role)
        with connection.cursor() as cursor:
            cursor.execute("SET ROLE ascua_app")
    yield
    connection_created.disconnect(_drop_to_app_role)
    with django_db_blocker.unblock(), connection.cursor() as cursor:
        cursor.execute("RESET ROLE")
