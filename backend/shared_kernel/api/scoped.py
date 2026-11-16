"""Base viewset for tenant-scoped resources: every request runs as its authenticated actor."""

from typing import Any

from django.db import models
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shared_kernel.domain.actor import Actor
from shared_kernel.infrastructure.actor_context import clear_actor, set_actor


def actor_from_request(request: Request) -> Actor:
    user = request.user
    if user is None or user.pk is None:
        raise NotAuthenticated
    return Actor(user_id=user.pk, is_admin=bool(getattr(user, "is_admin", False)))


class ScopedViewSet(GenericViewSet):  # type: ignore[type-arg]
    actor: Actor

    def initial(self, request: Request, *args: Any, **kwargs: Any) -> None:
        super().initial(request, *args, **kwargs)  # authentication and permissions first
        self.actor = actor_from_request(request)
        set_actor(self.actor)

    def finalize_response(
        self, request: Request, response: Response, *args: Any, **kwargs: Any
    ) -> Response:
        clear_actor()
        return super().finalize_response(request, response, *args, **kwargs)

    def get_queryset(self) -> models.QuerySet[Any]:
        return self.repository_queryset(self.actor)

    def repository_queryset(self, actor: Actor) -> models.QuerySet[Any]:
        raise NotImplementedError
