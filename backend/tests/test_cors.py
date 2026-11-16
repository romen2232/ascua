from django.test import override_settings
from rest_framework.test import APIClient

ORIGIN = "http://localhost:8081"


@override_settings(CORS_ALLOWED_ORIGINS=[ORIGIN])
def test_configured_origin_may_send_credentials(db):
    response = APIClient().options(
        "/api/auth/refresh",
        HTTP_ORIGIN=ORIGIN,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,x-ascua-client",
    )
    assert response["Access-Control-Allow-Origin"] == ORIGIN
    assert response["Access-Control-Allow-Credentials"] == "true"
    assert "x-ascua-client" in response["Access-Control-Allow-Headers"].lower()


@override_settings(CORS_ALLOWED_ORIGINS=[ORIGIN])
def test_unknown_origin_is_not_allowed(db):
    response = APIClient().get("/api/schema/", HTTP_ORIGIN="https://evil.example")
    assert "Access-Control-Allow-Origin" not in response
