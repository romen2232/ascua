"""Run every test as the runtime role so row-level security applies exactly as in production.

The test database is created and migrated as ascua_owner; after that every connection to it
switches to ascua_app.
"""

import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import pytest
from django.db import connection
from django.db.backends.signals import connection_created

from shared_kernel.domain.actor import Actor
from shared_kernel.infrastructure.actor_context import acting_as
from tests.fixtures.sample_notes.infrastructure.models import SampleNote


def _drop_to_app_role(sender: Any, connection: Any, **_: Any) -> None:
    if connection.settings_dict["NAME"].startswith("test_"):
        with connection.cursor() as cursor:
            cursor.execute("SET ROLE ascua_app")


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup: None, django_db_blocker: Any) -> Iterator[None]:
    with django_db_blocker.unblock():
        connection_created.connect(_drop_to_app_role)
        with connection.cursor() as cursor:
            # Test-only: lets transactional tests flush tables between tests.
            cursor.execute("GRANT TRUNCATE ON ALL TABLES IN SCHEMA public TO ascua_app")
            cursor.execute("SET ROLE ascua_app")
    yield
    connection_created.disconnect(_drop_to_app_role)
    with django_db_blocker.unblock(), connection.cursor() as cursor:
        cursor.execute("RESET ROLE")


@dataclass
class TwoUsers:
    a: Actor
    b: Actor


@pytest.fixture
def two_users_with_notes(db) -> TwoUsers:
    """A owns two notes, B owns one. Rows are inserted while acting as their owner."""
    users = TwoUsers(a=Actor(uuid.uuid4(), False), b=Actor(uuid.uuid4(), False))
    with acting_as(users.a):
        SampleNote.objects.for_actor(users.a).create(owner_id=users.a.user_id, text="a1")
        SampleNote.objects.for_actor(users.a).create(owner_id=users.a.user_id, text="a2")
    with acting_as(users.b):
        SampleNote.objects.for_actor(users.b).create(owner_id=users.b.user_id, text="b1")
    return users
