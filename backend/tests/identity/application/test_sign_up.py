import uuid
from datetime import timedelta

import pytest

from identity.application.invite import invite_user
from identity.application.sign_up import SignUpDeps, accept_invitation, confirm_totp
from identity.domain.email import Email
from identity.domain.errors import EmailTaken, EnrolmentInvalid, InvalidTotpCode, WeakPassword
from identity.domain.invitation import InvitationExpired, InvitationInvalid, InvitationUsed
from identity.domain.user import User
from shared_kernel.domain.actor import Actor
from shared_kernel.domain.errors import NotAllowed
from tests.identity.fakes import (
    FakeClock,
    FakeEnrolmentTokens,
    FakeInvitations,
    FakeTotp,
    FakeUsers,
)

PASSWORD = "correct horse battery"


@pytest.fixture
def deps() -> SignUpDeps:
    return SignUpDeps(
        FakeUsers(), FakeInvitations(), FakeClock(), FakeTotp(), FakeEnrolmentTokens()
    )


def admin(deps) -> Actor:
    user = User(
        uuid.uuid4(), Email("admin@example.com"), "Admin", "es", True, True, deps.clock.now()
    )
    deps.users.add(user, PASSWORD)
    return Actor(user.id, True)


def invite(deps, email="Friend@Example.com") -> str:
    return invite_user(admin(deps), Email(email), deps, token_factory=lambda: "tok")


def test_non_admin_cannot_invite(deps):
    with pytest.raises(NotAllowed):
        invite_user(Actor(uuid.uuid4(), False), Email("x@example.com"), deps, lambda: "t")


def test_invite_rejects_email_of_existing_user(deps):
    actor = admin(deps)
    with pytest.raises(EmailTaken):
        invite_user(actor, Email("ADMIN@example.com"), deps, lambda: "t")


def test_accept_invitation_creates_user_without_confirmed_totp(deps):
    raw = invite(deps)
    enrolment = accept_invitation(raw, "Friend", PASSWORD, "en", deps)
    user = deps.users.get(enrolment.user_id)
    assert user.email == Email("friend@example.com")
    assert user.locale == "en"
    assert user.is_admin is False
    assert user.totp_confirmed is False
    assert enrolment.provisioning_uri.startswith("otpauth://totp/")
    assert deps.enrolment.read(enrolment.enrolment_token) == user.id


def test_accept_unknown_token_raises_invalid(deps):
    with pytest.raises(InvitationInvalid):
        accept_invitation("nope", "Friend", PASSWORD, "es", deps)


def test_accept_used_invitation_raises(deps):
    raw = invite(deps)
    accept_invitation(raw, "Friend", PASSWORD, "es", deps)
    with pytest.raises(InvitationUsed):
        accept_invitation(raw, "Friend", PASSWORD, "es", deps)


def test_accept_expired_invitation_raises(deps):
    raw = invite(deps)
    deps.clock.advance(timedelta(days=7, seconds=1))
    with pytest.raises(InvitationExpired):
        accept_invitation(raw, "Friend", PASSWORD, "es", deps)


def test_accept_invitation_rejects_existing_email_in_other_case(deps):
    raw = invite(deps, "Friend@Example.com")
    other = User(
        uuid.uuid4(), Email("friend@example.com"), "F", "es", False, True, deps.clock.now()
    )
    deps.users.add(other, PASSWORD)
    with pytest.raises(EmailTaken):
        accept_invitation(raw, "Friend", PASSWORD, "es", deps)


def test_accept_invitation_rejects_short_password(deps):
    raw = invite(deps)
    with pytest.raises(WeakPassword):
        accept_invitation(raw, "Friend", "short", "es", deps)
    # The invitation is still usable after a rejected attempt.
    accept_invitation(raw, "Friend", PASSWORD, "es", deps)


def test_confirm_totp_with_valid_code_sets_confirmed(deps):
    enrolment = accept_invitation(invite(deps), "Friend", PASSWORD, "es", deps)
    confirm_totp(enrolment.enrolment_token, FakeTotp.VALID, deps)
    assert deps.users.get(enrolment.user_id).totp_confirmed is True


def test_confirm_totp_with_wrong_code_raises(deps):
    enrolment = accept_invitation(invite(deps), "Friend", PASSWORD, "es", deps)
    with pytest.raises(InvalidTotpCode):
        confirm_totp(enrolment.enrolment_token, "000000", deps)


def test_confirm_totp_twice_is_rejected(deps):
    enrolment = accept_invitation(invite(deps), "Friend", PASSWORD, "es", deps)
    confirm_totp(enrolment.enrolment_token, FakeTotp.VALID, deps)
    with pytest.raises(EnrolmentInvalid):
        confirm_totp(enrolment.enrolment_token, FakeTotp.VALID, deps)
