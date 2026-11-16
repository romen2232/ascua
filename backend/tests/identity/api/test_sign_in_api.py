from datetime import timedelta

import pytest
import time_machine
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APIClient

from identity.infrastructure.models import UserRecord

PASSWORD = "correct horse battery"
EMAIL = "romen@example.com"


@pytest.fixture
def user(db):
    record = UserRecord.objects.create_user(
        EMAIL, PASSWORD, display_name="Romen", totp_confirmed=True
    )
    TOTPDevice.objects.create(user=record, name="ascua", step=30, digits=6, tolerance=1)
    return record


def code_for(user, offset_seconds: int = 0) -> str:
    device = TOTPDevice.objects.get(user=user)
    with time_machine.travel(timedelta(seconds=offset_seconds), tick=False):
        return f"{totp(device.bin_key, step=device.step, digits=device.digits):06d}"


def password_step(client, email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/sign-in", {"email": email, "password": password}, format="json")


def totp_step(client, mfa_token, code, **extra):
    return client.post(
        "/api/auth/sign-in/totp", {"mfa_token": mfa_token, "code": code}, format="json", **extra
    )


def sign_in(user, **extra):
    client = APIClient()
    mfa = password_step(client).json()["mfa_token"]
    return client, totp_step(client, mfa, code_for(user), **extra)


def test_sign_in_wrong_password_and_unknown_email_return_same_error(user):
    wrong = password_step(APIClient(), password="not the password")
    unknown = password_step(APIClient(), email="nobody@example.com")
    assert wrong.status_code == unknown.status_code == 400
    assert wrong.json() == unknown.json()
    assert wrong.json()["error"]["code"] == "invalid_credentials"


def test_email_is_matched_case_insensitively(user):
    response = password_step(APIClient(), email="  Romen@Example.COM ")
    assert response.status_code == 200
    assert "mfa_token" in response.json()


def test_full_sign_in_returns_tokens(user):
    client, response = sign_in(user)
    assert response.status_code == 200, response.content
    body = response.json()
    assert body["access"]
    assert body["refresh"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {body['access']}")
    assert client.get("/api/me").json()["email"] == EMAIL


def test_totp_code_cannot_be_reused(user):
    client = APIClient()
    code = code_for(user)
    first = totp_step(client, password_step(client).json()["mfa_token"], code)
    assert first.status_code == 200
    second = totp_step(client, password_step(client).json()["mfa_token"], code)
    assert second.status_code == 400
    assert second.json()["error"]["code"] == "invalid_totp_code"


@pytest.mark.parametrize("offset", [-30, 30])
def test_totp_accepts_one_step_drift(user, offset):
    client = APIClient()
    mfa = password_step(client).json()["mfa_token"]
    assert totp_step(client, mfa, code_for(user, offset)).status_code == 200


def test_totp_rejects_two_steps_drift(user):
    client = APIClient()
    mfa = password_step(client).json()["mfa_token"]
    assert totp_step(client, mfa, code_for(user, 90)).status_code == 400


def test_expired_mfa_token_is_rejected(user):
    client = APIClient()
    mfa = password_step(client).json()["mfa_token"]
    with time_machine.travel(timedelta(minutes=6)):
        response = totp_step(client, mfa, code_for(user))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "mfa_invalid"


def test_sixth_failed_attempt_is_locked_out(user):
    for _ in range(4):
        assert password_step(APIClient(), password="wrong password!").status_code == 400
    # The fifth failure locks the email + IP pair.
    assert password_step(APIClient(), password="wrong password!").status_code == 429
    response = password_step(APIClient())  # correct password, still locked
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "locked_out"


def test_web_client_gets_refresh_cookie_not_body(user):
    _, response = sign_in(user, HTTP_X_ASCUA_CLIENT="web")
    assert response.status_code == 200
    assert "refresh" not in response.json()
    cookie = response.cookies["ascua_refresh"]
    assert cookie["httponly"]
    assert cookie["secure"]
    assert cookie["samesite"] == "Strict"
    assert cookie["path"] == "/api/auth/refresh"


def test_refresh_rotates_tokens(user):
    _, response = sign_in(user)
    refresh = response.json()["refresh"]
    rotated = APIClient().post("/api/auth/refresh", {"refresh": refresh}, format="json")
    assert rotated.status_code == 200
    assert rotated.json()["refresh"] != refresh
    reused = APIClient().post("/api/auth/refresh", {"refresh": refresh}, format="json")
    assert reused.status_code == 401


def test_web_refresh_reads_and_sets_cookie(user):
    client, response = sign_in(user, HTTP_X_ASCUA_CLIENT="web")
    refreshed = client.post("/api/auth/refresh", {}, format="json", HTTP_X_ASCUA_CLIENT="web")
    assert refreshed.status_code == 200, refreshed.content
    assert "access" in refreshed.json()
    assert "refresh" not in refreshed.json()
    assert refreshed.cookies["ascua_refresh"].value != response.cookies["ascua_refresh"].value


def test_sign_out_revokes_refresh(user):
    _, response = sign_in(user)
    refresh = response.json()["refresh"]
    out = APIClient().post("/api/auth/sign-out", {"refresh": refresh}, format="json")
    assert out.status_code == 204
    again = APIClient().post("/api/auth/refresh", {"refresh": refresh}, format="json")
    assert again.status_code == 401


def test_unconfirmed_totp_cannot_sign_in(user):
    user.totp_confirmed = False
    user.save()
    response = password_step(APIClient())
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "totp_not_enrolled"


def test_me_returns_only_caller(user):
    UserRecord.objects.create_user("other@example.com", PASSWORD, totp_confirmed=True)
    client, response = sign_in(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    assert client.get("/api/me").json() == {
        "id": str(user.id),
        "email": EMAIL,
        "display_name": "Romen",
        "locale": "es",
        "is_admin": False,
    }


def test_lockout_is_per_email(user):
    UserRecord.objects.create_user("other@example.com", PASSWORD, totp_confirmed=True)
    for _ in range(5):
        password_step(APIClient(), password="wrong password!")
    assert password_step(APIClient(), email="other@example.com").status_code == 200


def test_wrong_totp_codes_are_throttled(user):
    client = APIClient()
    mfa = password_step(client).json()["mfa_token"]
    assert totp_step(client, mfa, "000000").status_code == 400
    # The failure survives the request (django-otp backs off exponentially from it) ...
    assert TOTPDevice.objects.get(user=user).throttling_failure_count == 1
    # ... so while throttled, even the correct code is refused.
    assert totp_step(client, mfa, code_for(user)).status_code == 400
