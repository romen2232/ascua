import uuid
from datetime import UTC, datetime

import pytest
from django.db import IntegrityError, transaction

from identity.domain.email import Email
from identity.domain.invitation import Invitation
from identity.domain.user import User
from identity.infrastructure.models import UserRecord
from identity.infrastructure.repositories import DjangoInvitationRepository, DjangoUserRepository

NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)


def make_user(email="romen@example.com", is_admin=False) -> User:
    return User(uuid.uuid4(), Email(email), "Romen", "es", is_admin, False, NOW)


def test_user_round_trip(db):
    repo = DjangoUserRepository()
    user = make_user(is_admin=True)
    repo.add(user, "a long password")
    loaded = repo.get(user.id)
    assert loaded == user
    assert repo.get_by_email(Email(" ROMEN@example.com")) == user
    assert repo.get_by_email(Email("nobody@example.com")) is None


def test_user_save_updates_fields(db):
    repo = DjangoUserRepository()
    user = make_user()
    repo.add(user, "a long password")
    user.totp_confirmed = True
    user.display_name = "R"
    repo.save(user)
    assert repo.get(user.id).totp_confirmed is True
    assert repo.get(user.id).display_name == "R"


def test_password_hashed_with_argon2id(db):
    user = make_user()
    DjangoUserRepository().add(user, "a long password")
    record = UserRecord.objects.get(pk=user.id)
    assert record.password.startswith("argon2$argon2id$")
    assert record.check_password("a long password")


def test_unique_email_enforced_at_db_level(db):
    repo = DjangoUserRepository()
    repo.add(make_user(), "pw-1")
    with pytest.raises(IntegrityError), transaction.atomic():
        UserRecord.objects.create(email="romen@example.com")


def test_invitation_round_trip(db):
    admin = make_user(is_admin=True)
    DjangoUserRepository().add(admin, "pw")
    repo = DjangoInvitationRepository()
    invitation, raw = Invitation.issue(Email("friend@example.com"), admin.id, NOW, lambda: "t")
    repo.add(invitation)
    loaded = repo.get_by_token_hash(invitation.token_hash)
    assert loaded == invitation
    assert loaded is not None
    loaded.accept(raw, NOW)
    repo.save(loaded)
    reloaded = repo.get_by_token_hash(invitation.token_hash)
    assert reloaded is not None
    assert reloaded.used_at == NOW
    assert repo.get_by_token_hash("missing") is None
