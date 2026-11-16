import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from identity.domain.email import Email
from identity.domain.invitation import (
    Invitation,
    InvitationExpired,
    InvitationInvalid,
    InvitationUsed,
)

NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)
TOKEN = "raw-token-value"


def issue() -> tuple[Invitation, str]:
    return Invitation.issue(Email("friend@example.com"), uuid.uuid4(), NOW, lambda: TOKEN)


def test_issue_stores_only_hash():
    invitation, raw = issue()
    assert raw == TOKEN
    assert invitation.token_hash == hashlib.sha256(TOKEN.encode()).hexdigest()
    assert TOKEN not in repr(invitation)
    assert invitation.expires_at == NOW + timedelta(days=7)


def test_accept_marks_used():
    invitation, raw = issue()
    invitation.accept(raw, NOW + timedelta(days=1))
    assert invitation.used_at == NOW + timedelta(days=1)


def test_accept_twice_raises_used():
    invitation, raw = issue()
    invitation.accept(raw, NOW)
    with pytest.raises(InvitationUsed):
        invitation.accept(raw, NOW)


def test_accept_on_last_second_is_allowed():
    invitation, raw = issue()
    invitation.accept(raw, NOW + timedelta(days=7))


def test_accept_after_seven_days_raises_expired():
    invitation, raw = issue()
    with pytest.raises(InvitationExpired):
        invitation.accept(raw, NOW + timedelta(days=7, seconds=1))
    assert invitation.used_at is None


def test_accept_wrong_token_raises_invalid():
    invitation, _ = issue()
    with pytest.raises(InvitationInvalid):
        invitation.accept("other-token", NOW)


def test_error_statuses():
    assert InvitationInvalid.http_status == 404
    assert InvitationUsed.http_status == 410
    assert InvitationExpired.http_status == 410
