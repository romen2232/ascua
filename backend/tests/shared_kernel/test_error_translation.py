from rest_framework.test import APIClient

from identity.infrastructure.models import UserRecord
from tests.conftest import signed_in

URL = "/api/test/notes/"


def test_error_message_in_english_with_accept_language_en(db):
    response = APIClient().get(URL, HTTP_ACCEPT_LANGUAGE="en")
    assert response.json()["error"]["message"] == "Authentication is required."


def test_error_message_defaults_to_spanish(db):
    response = APIClient().get(URL)
    assert response.json()["error"]["message"] == "Hace falta iniciar sesión."


def test_error_message_uses_user_locale_without_accept_language(db):
    user = UserRecord.objects.create_user("en@example.com", "pw", locale="en")
    response = signed_in(user).get(f"{URL}00000000-0000-0000-0000-000000000000/")
    assert response.json()["error"]["message"] == "Not found."


def test_accept_language_wins_over_user_locale(db):
    user = UserRecord.objects.create_user("en@example.com", "pw", locale="en")
    response = signed_in(user).get(
        f"{URL}00000000-0000-0000-0000-000000000000/", HTTP_ACCEPT_LANGUAGE="es"
    )
    assert response.json()["error"]["message"] == "No encontrado."
