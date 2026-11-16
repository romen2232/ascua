"""Per-transaction actor context read by PostgreSQL row-level security policies.

The actor lives in transaction-local settings (`set_config(..., true)`), so it can never
outlive the transaction that set it.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from django.db import connection, transaction

from shared_kernel.domain.actor import Actor


def _write(user_id: str, is_admin: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('ascua.actor_id', %s, true),"
            " set_config('ascua.actor_is_admin', %s, true)",
            [user_id, is_admin],
        )


def set_actor(actor: Actor) -> None:
    if not connection.in_atomic_block:
        raise RuntimeError("set_actor must run inside a transaction")
    _write(str(actor.user_id), "true" if actor.is_admin else "false")


def clear_actor() -> None:
    """Forget the actor for the rest of the transaction (no-op if it is already broken)."""
    if connection.in_atomic_block and not connection.needs_rollback:
        _write("", "")


def current_actor() -> Actor | None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_setting('ascua.actor_id', true),"
            " current_setting('ascua.actor_is_admin', true)"
        )
        user_id, is_admin = cursor.fetchone()
    if not user_id:
        return None
    return Actor(UUID(user_id), is_admin == "true")


@contextmanager
def acting_as(actor: Actor) -> Iterator[Actor]:
    """Run a block as `actor`, restoring whatever actor was set before it on exit."""
    with transaction.atomic():
        previous = current_actor()
        set_actor(actor)
        try:
            yield actor
        finally:
            # A broken transaction is rolled back to the savepoint, which restores the setting.
            if previous is None:
                clear_actor()
            elif not connection.needs_rollback:
                set_actor(previous)
