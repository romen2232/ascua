"""Another user, admin or not, can never read or change an item they don't own."""

import pytest
from rest_framework.test import APIClient

from identity.infrastructure.models import UserRecord
from tests.isolation.registry import ROUTES

TENANT_CASES = [
    (name, method)
    for name, case in sorted(ROUTES.items())
    if case.kind == "tenant"
    for method in sorted(case.methods)
    if not (case.collection and method == "POST")  # creating in a collection acts on self
]


def _client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


def _attempt(client, method, url, payload):
    return getattr(client, method.lower())(url, payload, format="json")


def _check_isolation(owner, intruder, name, method):
    case = ROUTES[name]
    assert case.make_target is not None
    url, item_id = case.make_target(owner)
    before = _client(owner).get(url).content

    response = _attempt(_client(intruder), method, url, case.write_payload)

    if case.collection:
        assert response.status_code == 200
        assert item_id not in response.content.decode()
    else:
        assert response.status_code == 404, response.content
        assert item_id not in response.content.decode()
    assert _client(owner).get(url).content == before


@pytest.fixture
def owner(db):
    return UserRecord.objects.create_user("owner@example.com", "pw")


@pytest.fixture
def intruder(db):
    return UserRecord.objects.create_user("intruder@example.com", "pw")


@pytest.mark.parametrize(("name", "method"), TENANT_CASES)
def test_api_isolation(owner, intruder, name, method):
    _check_isolation(owner, intruder, name, method)


@pytest.mark.parametrize(("name", "method"), TENANT_CASES)
def test_admin_gets_404_on_other_users_item(owner, intruder, name, method):
    intruder.is_admin = True
    _check_isolation(owner, intruder, name, method)
