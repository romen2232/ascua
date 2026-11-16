import pytest
from rest_framework.test import APIClient

from identity.infrastructure.models import UserRecord

URL = "/api/test/notes/"


@pytest.fixture
def alice(db):
    return UserRecord.objects.create_user("alice@example.com", "pw")


@pytest.fixture
def bob(db):
    return UserRecord.objects.create_user("bob@example.com", "pw")


def client_for(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_list_returns_only_own_notes(alice, bob):
    client_for(alice).post(URL, {"text": "a1"}, format="json")
    client_for(bob).post(URL, {"text": "b1"}, format="json")
    response = client_for(alice).get(URL)
    assert response.status_code == 200
    assert [n["text"] for n in response.json()] == ["a1"]


def test_retrieve_other_users_note_returns_404(alice, bob):
    note_id = client_for(alice).post(URL, {"text": "a1"}, format="json").json()["id"]
    response = client_for(bob).get(f"{URL}{note_id}/")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_unauthenticated_returns_401_in_error_format(db):
    response = APIClient().get(URL)
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "not_authenticated"
    assert body["error"]["message"]
    assert body["error"]["fields"] is None


def test_domain_error_maps_to_400_with_code(alice):
    response = client_for(alice).post(URL, {"text": "   "}, format="json")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_value"


def test_validation_error_lists_fields(alice):
    response = client_for(alice).post(URL, {}, format="json")
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert "text" in error["fields"]


def test_actor_is_cleared_after_request(alice):
    from shared_kernel.infrastructure.actor_context import current_actor

    client_for(alice).get(URL)
    assert current_actor() is None
