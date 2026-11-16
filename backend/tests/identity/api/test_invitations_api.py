from datetime import timedelta
from io import StringIO

import pytest
import time_machine
from django.core.management import CommandError, call_command
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APIClient

from identity.infrastructure.models import UserRecord

PASSWORD = "correct horse battery"


@pytest.fixture
def admin_user(db):
    return UserRecord.objects.create_user(
        "admin@example.com", PASSWORD, is_admin=True, totp_confirmed=True
    )


@pytest.fixture
def member(db):
    return UserRecord.objects.create_user("member@example.com", PASSWORD, totp_confirmed=True)


def as_user(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def invite(admin_user, email="Friend@Example.com") -> str:
    response = as_user(admin_user).post("/api/invitations", {"email": email}, format="json")
    assert response.status_code == 201, response.content
    return str(response.json()["token"])


def accept(token, password=PASSWORD):
    return APIClient().post(
        "/api/invitations/accept",
        {"token": token, "display_name": "Friend", "password": password, "locale": "en"},
        format="json",
    )


def current_code(user_id) -> str:
    device = TOTPDevice.objects.get(user_id=user_id)
    return f"{totp(device.bin_key, step=device.step, digits=device.digits):06d}"


def test_non_admin_cannot_invite_returns_404(member):
    response = as_user(member).post("/api/invitations", {"email": "x@example.com"}, format="json")
    assert response.status_code == 404


def test_unauthenticated_cannot_invite(db):
    response = APIClient().post("/api/invitations", {"email": "x@example.com"}, format="json")
    assert response.status_code == 401


def test_accept_invitation_creates_user_without_confirmed_totp(admin_user):
    response = accept(invite(admin_user))
    assert response.status_code == 201, response.content
    body = response.json()
    assert body["provisioning_uri"].startswith("otpauth://totp/")
    user = UserRecord.objects.get(pk=body["user_id"])
    assert user.email == "friend@example.com"
    assert user.totp_confirmed is False


def test_accept_used_invitation_returns_410(admin_user):
    token = invite(admin_user)
    accept(token)
    response = accept(token)
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "invitation_used"
    assert UserRecord.objects.filter(email="friend@example.com").count() == 1


def test_accept_expired_invitation_returns_410(admin_user):
    token = invite(admin_user)
    with time_machine.travel(timedelta(days=7, seconds=5)):
        response = accept(token)
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "invitation_expired"
    assert not UserRecord.objects.filter(email="friend@example.com").exists()


def test_accept_invitation_rejects_existing_email_in_other_case(admin_user):
    token = invite(admin_user, "Friend@Example.com")
    UserRecord.objects.create_user("friend@example.com", PASSWORD)
    response = accept(token)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_taken"


def test_confirm_totp_with_valid_code_sets_confirmed(admin_user):
    body = accept(invite(admin_user)).json()
    response = APIClient().post(
        "/api/auth/totp/confirm",
        {"enrolment_token": body["enrolment_token"], "code": current_code(body["user_id"])},
        format="json",
    )
    assert response.status_code == 204, response.content
    assert UserRecord.objects.get(pk=body["user_id"]).totp_confirmed is True


def test_confirm_totp_with_expired_enrolment_token_returns_400(admin_user):
    body = accept(invite(admin_user)).json()
    with time_machine.travel(timedelta(minutes=16)):
        response = APIClient().post(
            "/api/auth/totp/confirm",
            {"enrolment_token": body["enrolment_token"], "code": current_code(body["user_id"])},
            format="json",
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "enrolment_invalid"


def test_ascua_init_creates_first_admin(db):
    out = StringIO()
    call_command("ascua_init", email="Owner@Example.com", password=PASSWORD, stdout=out)
    user = UserRecord.objects.get(email="owner@example.com")
    assert user.is_admin is True
    assert user.totp_confirmed is False
    assert "otpauth://totp/" in out.getvalue()
    assert "enrolment token" in out.getvalue().lower()


def test_ascua_init_refuses_when_users_exist(member):
    with pytest.raises(CommandError):
        call_command("ascua_init", email="owner@example.com", password=PASSWORD, stdout=StringIO())
