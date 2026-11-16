"""Row-level security checked with raw SQL as ascua_app, bypassing every Django manager."""

import uuid

import pytest
from django.db import DatabaseError, connection, transaction

from shared_kernel.infrastructure.actor_context import acting_as

TABLE = "sample_notes_samplenote"


def _count(owner=None) -> int:
    with connection.cursor() as c:
        if owner is None:
            c.execute(f"SELECT count(*) FROM {TABLE}")
        else:
            c.execute(f"SELECT count(*) FROM {TABLE} WHERE owner_id = %s", [owner])
        return int(c.fetchone()[0])


def test_rls_without_actor_returns_no_rows(two_users_with_notes):
    assert _count() == 0


def test_rls_other_actor_sees_nothing(two_users_with_notes):
    u = two_users_with_notes
    with acting_as(u.a):
        assert _count() == 2
        assert _count(u.b.user_id) == 0


def test_rls_blocks_insert_for_other_owner(two_users_with_notes):
    u = two_users_with_notes
    with (
        acting_as(u.a),
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as c,
    ):
        c.execute(
            f"INSERT INTO {TABLE} (id, owner_id, text) VALUES (%s, %s, 'x')",
            [uuid.uuid4(), u.b.user_id],
        )


def test_rls_blocks_update_moving_row_to_other_owner(two_users_with_notes):
    u = two_users_with_notes
    with (
        acting_as(u.a),
        pytest.raises(DatabaseError),
        transaction.atomic(),
        connection.cursor() as c,
    ):
        c.execute(f"UPDATE {TABLE} SET owner_id = %s", [u.b.user_id])


def test_table_forces_rls_for_its_owner(db):
    with connection.cursor() as c:
        c.execute(
            "SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname = %s", [TABLE]
        )
        assert c.fetchone() == (True, True)


def test_actor_does_not_outlive_acting_as_block(two_users_with_notes):
    with acting_as(two_users_with_notes.a):
        pass
    assert _count() == 0


@pytest.mark.django_db(transaction=True)
def test_actor_setting_does_not_leak_between_transactions():
    from shared_kernel.domain.actor import Actor
    from shared_kernel.infrastructure.actor_context import current_actor, set_actor

    with transaction.atomic():
        set_actor(Actor(uuid.uuid4(), False))
    with transaction.atomic():
        assert current_actor() is None
