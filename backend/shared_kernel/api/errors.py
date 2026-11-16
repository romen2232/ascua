"""One error shape for every API failure: {"error": {"code", "message", "fields"}}."""

import logging
from typing import Any

from django.http import Http404
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.views import set_rollback

from shared_kernel.domain.errors import DomainError

logger = logging.getLogger(__name__)

MESSAGES: dict[str, Any] = {
    "not_found": _("Not found."),
    "not_authenticated": _("Authentication is required."),
    "authentication_failed": _("Authentication failed."),
    "validation_error": _("Some fields are not valid."),
    "invalid_value": _("A value is not valid."),
    "currency_mismatch": _("Amounts in different currencies cannot be combined."),
    "method_not_allowed": _("This action is not allowed here."),
    "throttled": _("Too many attempts. Try again later."),
    "server_error": _("Something went wrong on the server."),
    "token_not_valid": _("Your session has expired. Sign in again."),
}


def register_messages(messages: dict[str, Any]) -> None:
    """Contexts register the user-facing message for each of their error codes."""
    MESSAGES.update(messages)


def message_for(code: str) -> str:
    return str(MESSAGES.get(code, MESSAGES["server_error"]))


def error_response(code: str, http_status: int, fields: Any = None) -> Response:
    body = {"error": {"code": code, "message": message_for(code), "fields": fields}}
    return Response(body, status=http_status)


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Accept-Language wins; otherwise the signed-in user's locale; otherwise Spanish."""
    request = context.get("request")
    user = getattr(request, "user", None)
    explicit = request is not None and "HTTP_ACCEPT_LANGUAGE" in request.META
    locale = getattr(user, "locale", None)
    if not explicit and locale:
        with translation.override(locale):
            return _handle(exc, context)
    return _handle(exc, context)


def _handle(exc: Exception, context: dict[str, Any]) -> Response:
    # Denied and missing look the same, so the API never confirms that something exists.
    if isinstance(exc, Http404 | exceptions.NotFound | exceptions.PermissionDenied):
        set_rollback()
        return error_response("not_found", status.HTTP_404_NOT_FOUND)
    if isinstance(exc, DomainError):
        if exc.rollback:
            set_rollback()
        return error_response(exc.code, exc.http_status)
    if isinstance(exc, exceptions.ValidationError):
        set_rollback()
        fields = exc.detail if isinstance(exc.detail, dict) else {"non_field_errors": exc.detail}
        return error_response("validation_error", status.HTTP_400_BAD_REQUEST, fields)

    response = drf_exception_handler(exc, context)
    if response is not None:
        assert isinstance(exc, exceptions.APIException)
        code = exc.get_codes() if isinstance(exc.get_codes(), str) else exc.default_code
        response.data = {"error": {"code": code, "message": message_for(str(code)), "fields": None}}
        return response

    logger.exception("Unhandled API error", exc_info=exc)
    set_rollback()
    return error_response("server_error", status.HTTP_500_INTERNAL_SERVER_ERROR)
