import uuid

import pytest

from shared_kernel.domain.actor import Actor
from shared_kernel.infrastructure.actor_context import acting_as, current_actor, set_actor
from shared_kernel.infrastructure.tenancy import UnscopedQueryError
from tests.fixtures.sample_notes.infrastructure.models import SampleNote


def test_tenant_manager_without_actor_raises(db):
    with pytest.raises(UnscopedQueryError):
        list(SampleNote.objects.all())


def test_for_actor_scopes_to_owner(two_users_with_notes):
    u = two_users_with_notes
    with acting_as(u.a):
        texts = sorted(n.text for n in SampleNote.objects.for_actor(u.a))
    assert texts == ["a1", "a2"]


@pytest.mark.django_db(transaction=True)
def test_set_actor_outside_transaction_raises():
    with pytest.raises(RuntimeError):
        set_actor(Actor(uuid.uuid4(), False))


def test_current_actor_round_trips(db):
    actor = Actor(uuid.uuid4(), True)
    with acting_as(actor):
        assert current_actor() == actor
    assert current_actor() is None


def test_nested_acting_as_restores_outer_actor(db):
    outer, inner = Actor(uuid.uuid4(), False), Actor(uuid.uuid4(), False)
    with acting_as(outer):
        with acting_as(inner):
            assert current_actor() == inner
        assert current_actor() == outer


def test_unscoped_for_system_rejects_unlisted_caller(db):
    with pytest.raises(PermissionError):
        SampleNote.objects.all_unscoped_for_system("test")
