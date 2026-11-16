"""Password check through Django's auth backends, throttled by django-axes."""

from typing import Any
from uuid import UUID

from axes.exceptions import AxesBackendPermissionDenied
from django.contrib.auth import authenticate
from django.http import HttpRequest, JsonResponse

from identity.domain.email import Email
from identity.domain.errors import LockedOut


class DjangoCredentialChecker:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def check(self, email: Email, password: str) -> UUID | None:
        try:
            # Keyed by `email` (USERNAME_FIELD): django-axes reads the username from that key.
            user = authenticate(self.request, email=email.value, password=password)
        except AxesBackendPermissionDenied as exc:
            raise LockedOut from exc
        if getattr(self.request, "axes_locked_out", False):
            raise LockedOut
        return user.pk if user is not None else None


def lockout_response(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
    """django-axes lockout response in the API's error format."""
    from shared_kernel.api.errors import message_for

    body = {"error": {"code": "locked_out", "message": message_for("locked_out"), "fields": None}}
    return JsonResponse(body, status=429)
