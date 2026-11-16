"""Every API route and every model must be declared here; the isolation suite enforces it.

When you add an endpoint, add a RouteCase. A `tenant` route gets a `make_target` that creates
an item owned by the given user and returns its URL and id, so the suite can check that nobody
else can reach it.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from shared_kernel.domain.actor import Actor
from shared_kernel.infrastructure.actor_context import acting_as
from tests.fixtures.sample_notes.infrastructure.models import SampleNote

Kind = Literal["tenant", "public", "self", "admin"]
Target = tuple[str, str]  # (url, id of the owned item)


@dataclass(frozen=True)
class RouteCase:
    methods: set[str]
    kind: Kind
    make_target: Callable[[Any], Target] | None = None
    collection: bool = False
    write_payload: dict[str, Any] = field(default_factory=dict)


def _actor(user: Any) -> Actor:
    return Actor(user.pk, bool(getattr(user, "is_admin", False)))


def _sample_note(user: Any) -> SampleNote:
    actor = _actor(user)
    with acting_as(actor):
        return SampleNote.objects.for_actor(actor).create(owner_id=user.pk, text="secret")


def sample_note_detail(user: Any) -> Target:
    note = _sample_note(user)
    return f"/api/test/notes/{note.pk}/", str(note.pk)


def sample_note_list(user: Any) -> Target:
    note = _sample_note(user)
    return "/api/test/notes/", str(note.pk)


ROUTES: dict[str, RouteCase] = {
    "schema": RouteCase({"GET"}, "public"),
    "invitation-create": RouteCase(
        {"POST"}, "admin", write_payload={"email": "someone@example.com"}
    ),
    "invitation-accept": RouteCase({"POST"}, "public"),
    "totp-confirm": RouteCase({"POST"}, "public"),
    "sign-in": RouteCase({"POST"}, "public"),
    "sign-in-totp": RouteCase({"POST"}, "public"),
    "token-refresh": RouteCase({"POST"}, "public"),
    "sign-out": RouteCase({"POST"}, "public"),
    "me": RouteCase({"GET"}, "self"),
    "sample-note-list": RouteCase(
        {"GET", "POST"}, "tenant", make_target=sample_note_list, collection=True
    ),
    "sample-note-detail": RouteCase({"GET"}, "tenant", make_target=sample_note_detail),
}

# Model label -> why it is not tenant-scoped.
TENANT_MODELS_EXEMPT: dict[str, str] = {
    "identity.UserRecord": "account table; access via /api/me and admin use cases only",
    "identity.InvitationRecord": "admin-issued; looked up only by token hash, holds no finances",
}

# Third-party apps whose tables hold no financial data.
EXEMPT_APP_LABELS = {"auth", "contenttypes", "otp_totp", "axes", "token_blacklist"}
